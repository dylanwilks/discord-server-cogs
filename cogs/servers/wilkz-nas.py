import discord
import subprocess
from enum import IntFlag, auto
from discord.ext import tasks, commands
from servercog import ServerCog


class WilkzNAS(
        ServerCog,
        name="wilkz-nas",
        description="Commands for wilkz-nas."
):
    class State(IntFlag):
        ACTIVE = auto()
        INACTIVE = auto()

    state_cooldown = commands.cooldown(1, 60.0)

    @commands.group(
        name="wilkz-nas",
        brief="Group of commands for wilkz-nas.",
        help="""
            Group composing of commands that wilkz-nas will respond to.
            So far contains only the wakeup command.
            """,
        invoke_without_command=True
    )
    async def wilkz_group(self, ctx: commands.Context):
        await ctx.send(f"Subcommand not found. Type in "
                       f"{self.bot.command_prefix}help {ctx.command} for a "
                       f"list of subcommands.")

    @wilkz_group.command(
        brief="Prints the state of wilkz-nas.",
        help="""
            Prints the state of wilkz-nas.
            """
    )
    @ServerCog.assert_perms(user_perm=0, channel_perm=0)
    async def state(
            self,
            ctx: commands.Context
    ) -> None:
        state = await super().get_state()
        await ctx.send(f"wilkz-nas state: {state.name}")

    @wilkz_group.command(
        name="wakeup",
        brief="Sends a magic packet to the server.",
        help="""
            Attempts to wake up wilkz-nas. Server will not
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
        await ctx.send(
            subprocess.check_output(
                ['/bin/sh',
                 '/root/discord-bot/scripts/wake-up.sh',
                 self._server_name
                 ],
                universal_newlines=True
            )
        )
        await asyncio.sleep(60)
        state = await super().get_state()
        if (state & self.State.INACTIVE):
            await ctx.send("No response detected after 60 seconds of sending "
                           "magic packet. Server altar-server is likely in an "
                           "unwakeable state.")

    @tasks.loop(seconds=30.0)
    async def check_state(self) -> None:
        host_state = subprocess.call(
            ['ping', '-c1', '-W1', 'wilkz-nas'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        state = await super().get_state()
        if (state & self.State.INACTIVE and host_state == 0):
            await super()._update_state(self.State.ACTIVE)
            server_channels = await super().get_channels()
            for channel_id in server_channels:
                channel = await self.bot.fetch_channel(channel_id)
                await channel.send("Response received from "
                                   "wilkz-nas. Server is active.")

            server_users = await super().get_users()
            for user_id in server_users:
                user = await self.bot.fetch_user(user_id)
                user_dm = await user.create_dm()
                await user_dm.send("Response received from "
                                   "wilkz-nas. Server is active.")

        elif (state & self.State.ACTIVE and host_state != 0):
            await super()._update_state(self.State.INACTIVE)
            server_channels = await super().get_channels()
            for channel_id in server_channels:
                channel = await self.bot.fetch_channel(channel_id)
                await channel.send("No response from wilkz-nas. "
                                   "Server is inactive.")

            server_users = await super().get_users()
            for user_id in server_users:
                user = await self.bot.fetch_user(user_id)
                user_dm = await user.create_dm()
                await user_dm.send("No response from wilkz-nas. "
                                   "Server is inactive.")

    async def cog_load(self) -> None:
        self.check_state.start()
        await super().cog_load()

    async def cog_unload(self) -> None:
        self.check_state.cancel()
        await super().cog_unload()


async def setup(bot) -> None:
    await bot.add_cog(WilkzNAS(bot))
