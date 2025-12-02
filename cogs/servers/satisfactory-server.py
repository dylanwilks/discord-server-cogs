import os
import asyncio
import subprocess
import discord
from enum import IntFlag, auto
from typing import Final
from discord.ext import tasks, commands
from lib.servercog import ServerCog
from lib.config import Config

SERVER_NAME: Final[str] = "satisfactory-server"
STATE_COOLDOWN: Final[float] = 60.0
CHECK_STATE_TIME: Final[float] = 30.0


class SatisfactoryServer(
        ServerCog,
        name=SERVER_NAME,
        description=f"Commands for {SERVER_NAME}."
):
    class State(IntFlag):
        ACTIVE = auto()
        INACTIVE = auto()
        HOST_INACTIVE = auto()

    state_cooldown = commands.cooldown(1, STATE_COOLDOWN)

    @commands.group(
        name=SERVER_NAME,
        brief=f"Group of commands for {SERVER_NAME}",
        help=f"""
            Group composing of commands that {SERVER_NAME} will respond to.
            Commands that change server state are issued using podman.
            Commands that interact with the server are issued using RCON.
            """,
        invoke_without_command=True
    )
    async def sf_group(self, ctx: commands.Context):
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await ctx.send(eval(constants.messages.servers.no_subcommand))

    @sf_group.command(
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
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        state = await super().get_state()
        await ctx.send(eval(constants.messages.servers.state))

    @sf_group.command(
        name="start",
        brief=f"Starts {SERVER_NAME}.",
        help=f"""
            Attempts to start the Satisfactory server {SERVER_NAME}.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    @ServerCog.assert_state(
        state=State.INACTIVE | State.HOST_INACTIVE
    )
    @state_cooldown
    async def sf_start(self, ctx: commands.Context) -> None:
        cog_config = Config.from_json(
            os.environ["BOT_COGS"]).servers[SERVER_NAME]
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        host_server = cog_config.host_server
        state = await super().get_state()
        if (state & self.State.HOST_INACTIVE):
            await ctx.send(eval(constants.messages.servers.host_inactive))
            await ctx.invoke(self.bot.get_command(f"{host_server} wakeup"))

        await ctx.send(eval(constants.messages.servers.start))
        config = Config.from_json(os.environ["BOT_CONFIG"])
        scripts_dir = config.dir.scripts
        await asyncio.create_subprocess_exec(
            f"{scripts_dir}/podman_up.sh",
            host_server,
            self.qualified_name,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    @sf_group.command(
        name="stop",
        brief="Stops the Satisfactory server.",
        help="""
            Stops the Satisfactory server {SERVER_NAME}. This will be
            necssary if the server is outdated.
            """
    )
    @ServerCog.assert_perms(user_perm=1, channel_perm=1)
    @ServerCog.assert_state(state=State.ACTIVE)
    @state_cooldown
    async def sf_stop(self, ctx: commands.Context) -> None:
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await ctx.send(eval(constants.messages.servers.stop))
        config = Config.from_json(os.environ["BOT_CONFIG"])
        cog_config = Config.from_json(
            os.environ["BOT_COGS"]).servers[SERVER_NAME]
        scripts_dir = config.dir.scripts
        host_server = cog_config.host_server
        await asyncio.create_subprocess_exec(
            f"{scripts_dir}/podman_down.sh",
            host_server,
            self.qualified_name,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    @tasks.loop(seconds=CHECK_STATE_TIME)
    async def check_state(self) -> None:
        config = Config.from_json(os.environ["BOT_CONFIG"])
        cog_config = Config.from_json(
            os.environ["BOT_COGS"]).servers[SERVER_NAME]
        scripts_dir = config.dir.scripts
        host_server = cog_config.host_server
        host_state = await asyncio.create_subprocess_exec(
            f"{scripts_dir}/ping_once.sh",
            host_server,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await host_state.wait()
        server_state = await asyncio.create_subprocess_exec(
            'nc', '-zv', '-w3', 'altar-server', '7777',
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await server_state.wait()
        state = await super().get_state()
        if ((state & (self.State.INACTIVE | self.State.HOST_INACTIVE)) and
                (not server_state.returncode)):
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

        elif ((state & (self.State.ACTIVE | self.State.INACTIVE)) and
              host_state.returncode):
            constants = Config.from_json(os.environ["BOT_CONSTANTS"])
            no_response = eval(constants.messages.servers.no_response)
            await super()._update_state(self.State.HOST_INACTIVE)
            server_channels = await super().get_channels()
            if (state & self.State.ACTIVE):
                for channel_id in server_channels:
                    channel = await self.bot.fetch_channel(channel_id)
                    await channel.send(no_response)

                server_users = await super().get_users()
                for user_id in server_users:
                    user = await self.bot.fetch_user(user_id)
                    user_dm = await user.create_dm()
                    await userdm.send(no_response)

        elif ((state & (self.State.ACTIVE | self.State.HOST_INACTIVE)) and
              (not host_state.returncode) and server_state.returncode):
            constants = Config.from_json(os.environ["BOT_CONSTANTS"])
            no_response = eval(constants.messages.servers.no_response)
            await super()._update_state(self.State.INACTIVE)
            server_channels = await super().get_channels()
            if (state & self.State.ACTIVE):
                for channel_id in server_channels:
                    channel = await self.bot.fetch_channel(channel_id)
                    await channel.send(no_response)

                server_users = await super().get_users()
                for user_id in server_users:
                    user = await self.bot.fetch_user(user_id)
                    user_dm = await user.create_dm()
                    await userdm.send(no_response)

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
    await bot.add_cog(SatisfactoryServer(bot))
