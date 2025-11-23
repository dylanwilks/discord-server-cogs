import subprocess
import asyncio
import discord
from enum import IntFlag, auto
from discord.ext import tasks, commands
from servercog import ServerCog


class AltarServer(
        ServerCog,
        name="altar-server",
        description="Commands for altar-server."
):
    class State(IntFlag):
        ACTIVE = auto()
        INACTIVE = auto()

    state_cooldown = commands.cooldown(1, 60.0)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        server_channels = await super().get_channels()
        if (server_channels and message.channel.id == server_channels[0]):
            channel = await self.bot.fetch_channel(server_channels[0])
            webhooks = await channel.webhooks()
            if (message.author.id == webhooks[0].id):
                server_users = await super().get_users()
                for user_id in server_users:
                    user = await self.bot.fetch_user(user_id)
                    user_dm = await user.create_dm()
                    await user_dm.send(message.content)

    @commands.group(
        name="altar-server",
        brief="Group of commands for altar-server.",
        help="""
            Group composing of commands that altar-server will
            respond to. These will primarily be state changing
            commands.
            """,
        invoke_without_command=True
    )
    async def altar_group(self, ctx: commands.Context):
        await ctx.send(f"Subcommand not found. Type in "
                       f"{self.bot.command_prefix}help {ctx.command} for a "
                       f"list of subcommands.")

    @altar_group.command(
        brief="Prints the state of altar-server.",
        help="""
            Prints the state of altar-server.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    async def state(
            self,
            ctx: commands.Context
    ) -> None:
        state = await super().get_state()
        await ctx.send(f"altar-server state: {state.name}")

    @altar_group.command(
        brief="Sends a magic packet to the server.",
        help="""
            Attempts to wake up altar-server. Server will not
            wake up if it is powered off and not hibernating.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    @ServerCog.assert_state(state=State.INACTIVE)
    @state_cooldown
    async def wakeup(
            self,
            ctx: commands.Context
    ) -> None:
        wakeup_server = await asyncio.create_subprocess_exec(
            '/bin/sh',
            '/root/discord-bot/scripts/wake-up.sh',
            'altar-server',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await wakeup_server.wait()
        out, _ = await wakeup_server.communicate()
        await ctx.send(str(out, 'utf-8'))
        time_passed = 0
        state = await super().get_state()
        while (state & self.State.INACTIVE and time_passed <= 180):
            await asyncio.sleep(10)
            state = await super().get_state()
            time_passed += 10

        if (state & self.State.INACTIVE):
            raise ServerCog.ServerError(
                f"Could not wake up server {self.qualified_name}.",
                self.qualified_name
            )

    @altar_group.command(
        name="hibernate",
        brief="Manually force the device into a hibernated state.",
        help="""
            Attempts to put the device into a hibernated state. Requires
            elevated privileges to use.
            """
    )
    @ServerCog.assert_perms(user_perm=1, channel_perm=1)
    @ServerCog.assert_state(state=State.ACTIVE)
    @state_cooldown
    async def altar_hibernate(
            self,
            ctx: commands.Context
    ) -> None:
        await asyncio.create_subprocess_exec(
            '/bin/sh',
            '/root/discord-bot/scripts/hibernate.sh',
            'altar-server',
            '&',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    @tasks.loop(seconds=30.0)
    async def check_state(self) -> None:
        host_state = await asyncio.create_subprocess_exec(
            'ping', '-c1', '-W1', 'altar-server',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        await host_state.wait()
        state = await super().get_state()
        if (state & self.State.INACTIVE and host_state.returncode == 0):
            await super()._update_state(self.State.ACTIVE)
            server_channels = await super().get_channels()
            for channel_id in server_channels:
                channel = await self.bot.fetch_channel(channel_id)
                await channel.send("Response received from "
                                   "altar-server. Server is active.")

            server_users = await super().get_users()
            for user_id in server_users:
                user = await self.bot.fetch_user(user_id)
                user_dm = await user.create_dm()
                await user_dm.send("Response received from "
                                   "altar-server. Server is active.")

        elif (state & self.State.ACTIVE and host_state.returncode != 0):
            await super()._update_state(self.State.INACTIVE)
            server_channels = await super().get_channels()
            for channel_id in server_channels:
                channel = await self.bot.fetch_channel(channel_id)
                await channel.send("No response from altar-server. "
                                   "Server is inactive.")

            server_users = await super().get_users()
            for user_id in server_users:
                user = await self.bot.fetch_user(user_id)
                user_dm = await user.create_dm()
                await user_dm.send("No response from altar-server. "
                                   "Server is inactive.")

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
    await bot.add_cog(AltarServer(bot))
