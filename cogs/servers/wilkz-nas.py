import os
import discord
import subprocess
import asyncio
from enum import IntFlag, auto
from typing import Final
from discord.ext import tasks, commands
from lib.servercog import ServerCog
from lib.config import Config

SERVER_NAME: Final[str] = "wilkz-nas"
STATE_COOLDOWN: Final[float] = 60.0
CHECK_STATE_TIME: Final[float] = 30.0


class WilkzNAS(
        ServerCog,
        name=SERVER_NAME,
        description=f"Commands for {SERVER_NAME}."
):
    class State(IntFlag):
        ACTIVE = auto()
        INACTIVE = auto()

    state_cooldown = commands.cooldown(1, STATE_COOLDOWN)

    @commands.group(
        name=SERVER_NAME,
        brief=f"Group of commands for {SERVER_NAME}.",
        help=f"""
            Group composing of commands that {SERVER_NAME} will respond to.
            """,
        invoke_without_command=True
    )
    async def wilkz_group(self, ctx: commands.Context):
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await ctx.send(eval(constants.messages.servers.no_subcommand))

    @wilkz_group.command(
        brief=f"Prints the state of {SERVER_NAME}.",
        help=f"""
            Prints the state of {SERVER_NAME}.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    async def state(
            self,
            ctx: commands.Context
    ) -> None:
        state = await super().get_state()
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await ctx.send(eval(constants.messages.servers.state))

    @wilkz_group.command(
        name="wakeup",
        brief="Sends a magic packet to the server.",
        help=f"""
            Attempts to wake up {SERVER_NAME}. Server will not
            wake up if it is inactive and in an unwakeable state.
            """
    )
    @ServerCog.assert_state(state=State.INACTIVE)
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    @state_cooldown
    async def wilkz_wakeup(
            self,
            ctx: commands.Context
    ) -> None:
        config = Config.from_json(os.environ["BOT_CONFIG"])
        cog_config = Config.from_json(os.environ["BOT_COGS"]).servers[SERVER_NAME]
        max_time = cog_config.max_start_time
        check_time = cog_config.check_start_time
        scripts_dir = config.dir.scripts
        wakeup_server = await asyncio.create_subprocess_exec(
            f"{scripts_dir}/wake-up.sh",
            self.qualified_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await wakeup_server.wait()
        out, _ = await wakeup_server.communicate()
        await ctx.send(str(out, 'utf-8'))
        time_passed = 0
        state = await super().get_state()
        while (state & self.State.INACTIVE and time_passed <= max_time):
            await asyncio.sleep(check_time)
            state = await super().get_state()
            time_passed += check_time

        if (state & self.State.INACTIVE):
            raise ServerCog.ServerError(
                f"Could not wake up server {self.qualified_name}.",
                self.qualified_name
            )

    @tasks.loop(seconds=CHECK_STATE_TIME)
    async def check_state(self) -> None:
        config = Config.from_json(os.environ["BOT_CONFIG"])
        scripts_dir = config.dir.scripts
        host_state = await asyncio.create_subprocess_exec(
            f"{scripts_dir}/ping_once.sh",
            self.qualified_name,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        await host_state.wait()
        state = await super().get_state()
        if (state & self.State.INACTIVE and host_state.returncode == 0):
            constants = Config.from_json(os.environ["BOT_CONSTANTS"])
            response = eval(constants.messages.servers.response)
            await super()._update_state(self.State.ACTIVE)
            server_channels = await super().get_channels()
            for channel_id in server_channels:
                channel = await self.bot.fetch_channel(channel_id)
                await channel.send(response)

            server_users = await super().get_users()
            for user_id in server_users:
                user = await self.bot.fetch_user(user_id)
                user_dm = await user.create_dm()
                await user_dm.send(response)

        elif (state & self.State.ACTIVE and host_state.returncode != 0):
            constants = Config.from_json(os.environ["BOT_CONSTANTS"])
            no_response = eval(constants.messages.servers.no_response)
            await super()._update_state(self.State.INACTIVE)
            server_channels = await super().get_channels()
            for channel_id in server_channels:
                channel = await self.bot.fetch_channel(channel_id)
                await channel.send(no_response)

            server_users = await super().get_users()
            for user_id in server_users:
                user = await self.bot.fetch_user(user_id)
                user_dm = await user.create_dm()
                await user_dm.send(no_response)

    @check_state.before_loop
    async def before_check_state(self):
        await self.bot.wait_until_ready()

    async def cog_load(self) -> None:
        self.check_state.start()
        await super().cog_load()

    async def cog_unload(self) -> None:
        self.check_state.cancel()
        await super().cog_unload()


async def setup(bot) -> None:
    await bot.add_cog(WilkzNAS(bot))
