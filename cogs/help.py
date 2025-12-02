import os
import sys
import sqlite3
import discord
from typing import Mapping, Optional, Any, List, Sequence
from discord.ext import commands
from lib.config import Config


class Help(commands.DefaultHelpCommand):
    def get_ending_note(self):
        return (f"!{self.invoked_with} "
                f"[command] for more information.")

    async def send_cog_help(self, cog: commands.Cog) -> None:
        for command in cog.get_commands():
            if (isinstance(command, commands.Group) and
                    command.qualified_name == cog.qualified_name):
                await self.send_group_help(command)
                return

            filtered = await self.filter_commands(cog.get_commands())
            if (not filtered):
                return

            self.add_indented_commands(
                cog.get_commands(),
                heading=self.commands_heading
            )
            note = self.get_ending_note()
            self.paginator.add_line()
            self.paginator.add_line(note)
            await self.send_pages()

    async def send_group_help(
            self,
            group: commands.Group[Any, ..., Any]
    ) -> None:
        if (await group.can_run(self.context)):
            self.add_command_formatting(group)
            self.add_indented_commands(
                group.commands,
                heading=self.commands_heading
            )

            note = self.get_ending_note()
            self.paginator.add_line()
            self.paginator.add_line(note)
            await self.send_pages()

    async def send_command_help(self, command: commands.Command) -> None:
        check_command = command
        if (command.parent is not None):
            check_command = command.parent

        if (await command.can_run(self.context)):
            self.add_command_formatting(command)
            self.paginator.close_page()
            await self.send_pages()


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._help_command = Help()
        self._help_command.cog = self
        self._original_help_command = bot.help_command
        bot.help_command = self._help_command

        async def predicate(ctx: commands.Context) -> bool:
            config = Config.from_json(os.environ["BOT_CONFIG"])
            sql_dir = config.dir.sql
            db_path = os.environ["BOT_DB"]
            db = sqlite3.connect(db_path, check_same_thread=False)
            db.execute("PRAGMA FOREIGN_KEYS = ON")
            cursor = db.cursor()
            def pull_singleton(x): return x[0]
            if isinstance(ctx.channel, discord.channel.DMChannel):
                with (
                    open(f"{sql_dir}/select_users_table.sql", "r")
                        as sql_select_users_table,
                    open(f"{sql_dir}/select_admins_table.sql", "r")
                        as sql_select_admins_table,
                ):
                    get_users = sql_select_users_table.read()
                    get_admins = sql_select_admins_table.read()

                cursor.execute(get_users)
                user_records = cursor.fetchall()
                cursor.execute(get_admins)
                admin_records = cursor.fetchall()
                db.close()
                users = tuple(map(pull_singleton, user_records))
                admins = tuple(map(pull_singleton, admin_records))
                return ((ctx.author.id in users) or (ctx.author.id in admins))
            else:
                with (
                    open(f"{sql_dir}/select_channels_table.sql", "r")
                        as sql_select_channels_table,
                ):
                    get_channels = sql_select_channels_table.read()

                cursor.execute(get_channels)
                channel_records = cursor.fetchall()
                db.close()
                channels = tuple(map(pull_singleton, channel_records))
                return ctx.channel.id in channels

        bot.help_command.add_check(predicate)

    def cog_unload(self) -> None:
        self.bot.help_command = self._original_help_command


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCog(bot))
