import asyncio
import subprocess
import discord
import time
from enum import IntFlag, auto
from discord.ext import tasks, commands
from servercog import ServerCog


class ProjectZomboidServer(
        ServerCog,
        name="pz-server",
        description="Commands for pz-server."
):
    class State(IntFlag):
        ACTIVE = auto()
        INACTIVE = auto()
        HOST_INACTIVE = auto()

    state_cooldown = commands.cooldown(1, 60.0)

    @commands.group(
        name="pz-server",
        brief="Group of commands for pz-server.",
        help="""
            Group composing of commands that pz-server will respond to.
            Commands that change server state are issued using podman.
            Commands that interact with the server are issued using RCON.
            """,
        invoke_without_command=True
    )
    async def pz_group(self, ctx: commands.Context):
        await ctx.send(f"Subcommand not found. Type in "
                       f"{self.bot.command_prefix}help {ctx.command} for a "
                       f"list of subcommands.")

    @pz_group.command(
        brief="Prints the state of pz-server.",
        help="""
            Prints the state of pz-server.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    async def state(
            self,
            ctx: commands.Context
    ) -> None:
        state = await super().get_state()
        await ctx.send(f"pz-server state: {state.name}")

    @pz_group.command(
        name="start",
        brief="Starts the Project Zomboid server.",
        help="""
            Attempts to start the Project Zomboid server. Server
            will not start if the host device altar-server is inactive
            and in an unwakeable state.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    @ServerCog.assert_state(
        state=State.INACTIVE | State.HOST_INACTIVE
    )
    @state_cooldown
    async def pz_start(self, ctx: commands.Context) -> None:
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
                    "magic packet. Host altar-server is likely in an "
                    "unwakeable state."
                )
                return

        await ctx.send("Starting pz-server...")
        subprocess.check_output(
            ['/bin/sh',
             '/root/discord-bot/scripts/podman_up.sh',
             'altar-server',
             'pz-server'
             ],
            universal_newlines=True
        )

    @pz_group.command(
        name="stop",
        brief="Stops the Project Zomboid server.",
        help="""
            Stops the Project Zomboid server. This will
            be necessary if mods are outdated.
            """
    )
    @ServerCog.assert_perms(user_perm=1, channel_perm=1)
    @ServerCog.assert_state(state=State.ACTIVE)
    @state_cooldown
    async def pz_stop(self, ctx: commands.Context) -> None:
        await ctx.send("Stopping pz-server...")
        subprocess.check_output(
            ['/bin/sh',
             '/root/discord-bot/scripts/podman_down.sh',
             'altar-server',
             'pz-server'
             ],
            universal_newlines=True
        )

    @pz_group.command(
        name="players",
        brief="Lists active players.",
        help="""
            Returns the name of active players.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    @ServerCog.assert_state(state=State.ACTIVE)
    async def pz_players(self, ctx: commands.Context) -> None:
        await ctx.send(
            subprocess.check_output(
                ['/bin/sh',
                 '/root/discord-bot/scripts/rcon.sh',
                 'pz-server',
                 'project-zomboid-server',
                 'players'
                 ],
                universal_newlines=True
            )
        )

    @tasks.loop(seconds=30.0)
    async def check_state(self) -> None:
        host_state1 = subprocess.call(
            ['ping', '-c1', '-W1', 'altar-server'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        server_state = subprocess.call(
            ['nc', '-zv', '-u', '-w1', 'altar-server', '16261'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        host_state2 = subprocess.call(
            ['ping', '-c1', '-W1', 'altar-server'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        state = await super().get_state()
        if ((state & (self.State.INACTIVE | self.State.HOST_INACTIVE)) and
                (not (host_state1 | server_state | host_state2))):
            await super()._update_state(self.State.ACTIVE)
            server_channels = await super().get_channels()
            for channel_id in server_channels:
                channel = await self.bot.fetch_channel(channel_id)
                await channel.send("Response received from "
                                   "pz-server. Server is active.")

            server_users = await super().get_users()
            for user_id in server_users:
                user = await self.bot.fetch_user(user_id)
                user_dm = await user.create_dm()
                await user_dm.send("Response received from "
                                   "pz-server. Server is active.")

        elif ((state & (self.State.ACTIVE | self.State.INACTIVE)) and
              host_state2):
            await super()._update_state(self.State.HOST_INACTIVE)
            server_channels = await super().get_channels()
            if (state & self.State.ACTIVE):
                for channel_id in server_channels:
                    channel = await self.bot.fetch_channel(channel_id)
                    await channel.send(
                        f"No response from pz-server. "
                        f"Server is inactive."
                    )

                server_users = await super().get_users()
                for user_id in server_users:
                    user = await self.bot.fetch_user(user_id)
                    user_dm = await user.create_dm()
                    await user_dm.send(
                        f"No response from pz-server. "
                        f"Server is inactive."
                    )

        elif ((state & (self.State.ACTIVE | self.State.HOST_INACTIVE)) and
              server_state):
            await super()._update_state(self.State.INACTIVE)
            server_channels = await super().get_channels()
            if (state & self.State.ACTIVE):
                for channel_id in server_channels:
                    channel = await self.bot.fetch_channel(channel_id)
                    await channel.send(f"No response from pz-server. "
                                       f"Server is inactive.")

                server_users = await super().get_users()
                for user_id in server_users:
                    user = await self.bot.fetch_user(user_id)
                    user_dm = await user.create_dm()
                    await user_dm.send(f"No response from pz-server. "
                                       f"Server is inactive.")

    async def cog_load(self) -> None:
        self.check_state.start()
        await super().cog_load()

    async def cog_unload(self) -> None:
        self.check_state.cancel()
        await super().cog_unload()


async def setup(bot) -> None:
    await bot.add_cog(ProjectZomboidServer(bot))
