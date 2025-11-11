import subprocess
import discord
from discord.ext import tasks, commands
from alerts import Alerts
from basecog import BaseCog


class BotControls(
        BaseCog,
        name="bot-controls",
        description="Technical controls for the bot."
):
    @commands.group(
        name="bot",
        invoke_without_command=True,
        brief="Group of commands for controlling the bot files.",
        help="""
            Group composing of commands for controlling the bot.
            Currently only includes commands that control cogs
            and extensions.
            """
    )
    @commands.cooldown(1, 5, commands.BucketType.default)
    async def control_group(self, ctx: commands.Context) -> None:
        await ctx.send("Subcommand not found.")

    @control_group.command(
        name="load-extension",
        brief="Loads an extension",
        help="""
            Loads an extension."
            """
    )
    async def load_extension(
            self,
            ctx: commands.Context,
            extension_name: str = commands.parameter(
                description="Name of extension to load"
            )
    ) -> None:
        try:
            await self.bot.load_extension(extension_name)
            print(f"Loaded extension {extension_name}")
            await ctx.send(f"Loaded extension {extension_name}.")
        except commands.ExtensionError as e:
            print(f"Failed to load extension {extension_name}: {e}")
            await ctx.send(f"Failed to load extension {extension_name}. "
                           f"Please check logs for error info.")

    @control_group.command(
        name="unload-extension",
        brief="Unloads an extension",
        help="""
            Unloads an extension."
            """
    )
    async def unload_extension(
            self,
            ctx: commands.Context,
            extension_name: str = commands.parameter(
                description="Name of extension to unload"
            )
    ) -> None:
        try:
            await self.bot.unload_extension(extension_name)
            print(f"Unloaded extension {extension_name}")
            await ctx.send(f"Unloaded extension {extension_name}.")
        except commands.ExtensionError as e:
            print(f"Failed to unload extension {extension_name}: {e}")
            await ctx.send(f"Failed to unload extension {extension_name}. "
                           f"Please check logs for error info.")

    @control_group.command(
        name="reload-extension",
        brief="Reloads an extension",
        help="""
            Reloads an extension."
            """
    )
    async def reload_extension(
            self,
            ctx: commands.Context,
            extension_name: str = commands.parameter(
                description="Name of extension to reload"
            )
    ) -> None:
        try:
            await self.bot.reload_extension(extension_name)
            print(f"Reloaded extension {extension_name}")
            await ctx.send(f"Reloaded extension {extension_name}.")
        except commands.ExtensionError as e:
            print(f"Failed to reload extension {extension_name}: {e}")
            await ctx.send(f"Failed to reload extension {extension_name}. "
                           f"Please check logs for error info.")

    async def cog_load(self) -> None:
        self.register_commands()
        await self.create_webhooks()
        print(f"Loaded cog {self.qualified_name}.")

    async def cog_unload(self) -> None:
        print(f"Unloaded cog {self.qualified_name}.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BotControls(bot))
