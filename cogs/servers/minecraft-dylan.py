import asyncio
import subprocess
import discord
import time
import re
from enum import IntFlag, auto
from discord.ext import tasks, commands
from servercog import ServerCog


class MinecraftDylanServer(
        ServerCog,
        name="minecraft-dylan",
        description="Commands for minecraft-dylan."
):
    class State(IntFlag):
        ACTIVE = auto()
        INACTIVE = auto()
        HOST_INACTIVE = auto()

    state_cooldown = commands.cooldown(1, 60.0)

    @commands.group(
        name="minecraft-dylan",
        brief="Group of commands for minecraft-dylan",
        help="""
            Group composing of commands that minecraft-dylan will respond to.
            Commands that change server state are issued using podman.
            Commands that interact with the server are issued using RCON.
            """,
        invoke_without_command=True
    )
    async def mc_group(self, ctx: commands.Context):
        await ctx.send(f"Subcommand not found. Type in "
                       f"{self.bot.command_prefix}help {ctx.command} for a "
                       f"list of subcommands.")

    @mc_group.command(
        brief="Prints the state of minecraft-dylan.",
        help="""
            Prints the state of minecraft-dylan.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    async def state(
            self,
            ctx: commands.Context
    ) -> None:
        state = await super().get_state()
        await ctx.send(f"minecraft-dylan state: {state.name}")

    @mc_group.command(
        name="start",
        brief="Starts the minecraft-dylan server.",
        help="""
            Attempts to start the minecraft-dylan server. Server
            will not start if the host device minecraft-dylan is inactive
            and in an unwakeable state.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    @ServerCog.assert_state(
        state=State.INACTIVE | State.HOST_INACTIVE
    )
    @state_cooldown
    async def mc_start(self, ctx: commands.Context) -> None:
        state = await super().get_state()
        if (state & self.State.HOST_INACTIVE):
            await ctx.send("Host server altar-server is inactive. "
                           "Sending magic packet...")
            await ctx.send(
                subprocess.check_output(
                    ['/bin/sh',
                     '/root/discord-bot/scripts/wake-up.sh',
                     'altar-server'
                     ],
                    universal_newlines=True
                )
            )
            await asyncio.sleep(60)
            state = await super().get_state()
            if (state & self.State.HOST_INACTIVE):
                await ctx.send(
                    "No response detected after 60 seconds of sending "
                    "magic packet. Host minecraft-dylan is likely in an "
                    "unwakeable state."
                )
                return

        await ctx.send("Starting minecraft-dylan...")
        subprocess.check_output(
            ['/bin/sh',
             '/root/discord-bot/scripts/podman_up.sh',
             'altar-server',
             'minecraft-dylan'
             ],
            universal_newlines=True
        )

    @mc_group.command(
        name="stop",
        brief="Stops the minecraft-dylan server.",
        help="""
            Stops the minecraft-dylan server. This will
            be necessary if mods are outdated.
            """
    )
    @ServerCog.assert_perms(user_perm=1, channel_perm=1)
    @ServerCog.assert_state(state=State.ACTIVE)
    @state_cooldown
    async def mc_stop(self, ctx: commands.Context) -> None:
        await ctx.send("Stopping minecraft-dylan...")
        subprocess.check_output(
            ['/bin/sh',
             '/root/discord-bot/scripts/podman_down.sh',
             'altar-server',
             'minecraft-dylan'
             ],
            universal_newlines=True
        )

    @mc_group.command(
        name="players",
        brief="Lists active players.",
        help="""
            Returns the name of active players.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    @ServerCog.assert_state(state=State.ACTIVE)
    async def mc_players(self, ctx: commands.Context) -> None:
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        await ctx.send(
            ansi_escape.sub('',
                            subprocess.check_output(
                                ['/bin/sh',
                                 '/root/discord-bot/scripts/rcon.sh',
                                 'minecraft-dylan',
                                 '1.21.1-mod',
                                 'list'
                                 ],
                                universal_newlines=True
                            )
                            )
        )

    @tasks.loop(seconds=30.0)
    async def check_state(self) -> None:
        host_state = subprocess.call(
            ['ping', '-c1', '-W1', 'altar-server'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        server_state = subprocess.call(
            ['nc', '-zv', '-w3', 'altar-server', '25565'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        state = await super().get_state()
        if ((state & (self.State.INACTIVE | self.State.HOST_INACTIVE)) and
                (not server_state)):
            await super()._update_state(self.State.ACTIVE)
            server_channels = await super().get_channels()
            for channel_id in server_channels:
                channel = await self.bot.fetch_channel(channel_id)
                await channel.send("Response received from "
                                   "minecraft-dylan. Server is active.")

            server_users = await super().get_users()
            for user_id in server_users:
                user = await self.bot.fetch_user(user_id)
                user_dm = await user.create_dm()
                await user_dm.send("Response received from "
                                   "minecraft-dylan. Server is active.")

        elif ((state & (self.State.ACTIVE | self.State.INACTIVE)) and
              host_state):
            await super()._update_state(self.State.HOST_INACTIVE)
            server_channels = await super().get_channels()
            if (state & self.State.ACTIVE):
                for channel_id in server_channels:
                    channel = await self.bot.fetch_channel(channel_id)
                    await channel.send(
                        f"No response from minecraft-dylan. "
                        f"Server is inactive."
                    )

                server_users = await super().get_users()
                for user_id in server_users:
                    user = await self.bot.fetch_user(user_id)
                    user_dm = await user.create_dm()
                    await user_dm.send(
                        f"No response from minecraft-dylan. "
                        f"Server is inactive."
                    )

        elif ((state & (self.State.ACTIVE | self.State.HOST_INACTIVE)) and
              (not host_state) and server_state):
            await super()._update_state(self.State.INACTIVE)
            server_channels = await super().get_channels()
            if (state & self.State.ACTIVE):
                for channel_id in server_channels:
                    channel = await self.bot.fetch_channel(channel_id)
                    await channel.send(f"No response from minecraft-dylan. "
                                       f"Server is inactive.")

                server_users = await super().get_users()
                for user_id in server_users:
                    user = await self.bot.fetch_user(user_id)
                    user_dm = await user.create_dm()
                    await user_dm.send(f"No response from minecraft-dylan. "
                                       f"Server is inactive.")

    async def cog_load(self) -> None:
        self.check_state.start()
        await super().cog_load()

    async def cog_unload(self) -> None:
        self.check_state.cancel()
        await super().cog_unload()


async def setup(bot) -> None:
    await bot.add_cog(MinecraftDylanServer(bot))
