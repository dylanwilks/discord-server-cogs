import asyncio
import subprocess
import discord
import time
import re
from enum import IntFlag, auto
from discord.ext import tasks, commands
from servercog import ServerCog


class SatisfactoryServer(
        ServerCog,
        name="satisfactory-server",
        description="Commands for satisfactory-server."
):
    class State(IntFlag):
        ACTIVE = auto()
        INACTIVE = auto()
        HOST_INACTIVE = auto()

    state_cooldown = commands.cooldown(1, 60.0)

    @commands.group(
        name="satisfactory-server",
        brief="Group of commands for satisfactory-server",
        help="""
            Group composing of commands that satisfactory-server will respond to.
            Commands that change server state are issued using podman.
            Commands that interact with the server are issued using RCON.
            """,
        invoke_without_command=True
    )
    async def sf_group(self, ctx: commands.Context):
        await ctx.send(f"Subcommand not found. Type in "
                       f"{self.bot.command_prefix}help {ctx.command} for a "
                       f"list of subcommands.")

    @sf_group.command(
        brief="Prints the state of satisfactory-server.",
        help="""
            Prints the state of satisfactory-server.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    async def state(
            self,
            ctx: commands.Context
    ) -> None:
        state = await super().get_state()
        await ctx.send(f"satisfactory-server state: {state.name}")

    @sf_group.command(
        name="start",
        brief="Starts the Satisfactory server.",
        help="""
            Attempts to start the Satisfactory server. Server
            will not start if the host device satisfactory-server is inactive
            and in an unwakeable state.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    @ServerCog.assert_state(
        state=State.INACTIVE | State.HOST_INACTIVE
    )
    @state_cooldown
    async def sf_start(self, ctx: commands.Context) -> None:
        state = await super().get_state()
        if (state & self.State.HOST_INACTIVE):
            await ctx.send("Host server altar-server is inactive. "
                           "Sending magic packet...")
            await ctx.invoke(self.bot.get_command('altar-server wakeup'))

        await ctx.send("Starting satisfactory-server...")
        await asyncio.create_subprocess_exec(
            '/bin/sh',
            '/root/discord-bot/scripts/podman_up.sh',
            'altar-server',
            'satisfactory-server',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    @sf_group.command(
        name="stop",
        brief="Stops the Satisfactory server.",
        help="""
            Stops the Satisfactory server.
            """
    )
    @ServerCog.assert_perms(user_perm=1, channel_perm=1)
    @ServerCog.assert_state(state=State.ACTIVE)
    @state_cooldown
    async def sf_stop(self, ctx: commands.Context) -> None:
        await ctx.send("Stopping satisfactory-server...")
        await asyncio.create_subprocess_exec(
            '/bin/sh',
            '/root/discord-bot/scripts/podman_down.sh',
            'altar-server',
            'satisfactory-server',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    @tasks.loop(seconds=30.0)
    async def check_state(self) -> None:
        host_state = await asyncio.create_subprocess_exec(
            'ping', '-c1', '-W1', 'altar-server',
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
            await super()._update_state(self.State.ACTIVE)
            server_channels = await super().get_channels()
            for channel_id in server_channels:
                channel = await self.bot.fetch_channel(channel_id)
                await channel.send("Response received from "
                                   "satisfactory-server. Server is active.")

            server_users = await super().get_users()
            for user_id in server_users:
                user = await self.bot.fetch_user(user_id)
                user_dm = await user.create_dm()
                await user_dm.send("Response received from "
                                   "satisfactory-server. Server is active.")

        elif ((state & (self.State.ACTIVE | self.State.INACTIVE)) and
              host_state.returncode):
            await super()._update_state(self.State.HOST_INACTIVE)
            server_channels = await super().get_channels()
            if (state & self.State.ACTIVE):
                for channel_id in server_channels:
                    channel = await self.bot.fetch_channel(channel_id)
                    await channel.send(
                        f"No response from satisfactory-server. "
                        f"Server is inactive."
                    )

                server_users = await super().get_users()
                for user_id in server_users:
                    user = await self.bot.fetch_user(user_id)
                    user_dm = await user.create_dm()
                    await user_dm.send(
                        f"No response from satisfactory-server. "
                        f"Server is inactive."
                    )

        elif ((state & (self.State.ACTIVE | self.State.HOST_INACTIVE)) and
              (not host_state.returncode) and server_state.returncode):
            await super()._update_state(self.State.INACTIVE)
            server_channels = await super().get_channels()
            if (state & self.State.ACTIVE):
                for channel_id in server_channels:
                    channel = await self.bot.fetch_channel(channel_id)
                    await channel.send(f"No response from satisfactory-server. "
                                       f"Server is inactive.")

                server_users = await super().get_users()
                for user_id in server_users:
                    user = await self.bot.fetch_user(user_id)
                    user_dm = await user.create_dm()
                    await user_dm.send(f"No response from satisfactory-server. "
                                       f"Server is inactive.")

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
