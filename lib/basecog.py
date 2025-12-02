import os
import sys
import sqlite3
import traceback
import discord
from typing import Tuple, List
from datetime import datetime
from discord.ext import commands
from lib.config import Config


class BaseCog(commands.Cog):
    instances = 0

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        with (
            open(f"{sql_dir}/create_users.sql", "r")
                as sql_create_users,
            open(f"{sql_dir}/create_channels.sql", "r")
                as sql_create_channels,
            open(f"{sql_dir}/create_commands.sql", "r")
                as sql_create_commands,
            open(f"{sql_dir}/create_user_commands.sql", "r")
                as sql_create_user_commands,
            open(f"{sql_dir}/create_channel_commands.sql", "r")
                as sql_create_channel_commands,
            open(f"{sql_dir}/create_cogs.sql", "r")
                as sql_create_cogs,
            open(f"{sql_dir}/create_user_cogs.sql", "r")
                as sql_create_user_cogs,
            open(f"{sql_dir}/create_channel_cogs.sql", "r")
                as sql_create_channel_cogs,
            open(f"{sql_dir}/create_admins.sql", "r")
                as sql_create_admins,
            open(f"{sql_dir}/insert_cog.sql", "r")
                as sql_insert_cog,
        ):
            create_users_table = sql_create_users.read()
            create_channels_table = sql_create_channels.read()
            create_commands_table = sql_create_commands.read()
            create_user_commands_table = sql_create_user_commands.read()
            create_channel_commands_table = sql_create_channel_commands.read()
            create_cogs_table = sql_create_cogs.read()
            create_user_cogs_table = sql_create_user_cogs.read()
            create_channel_cogs_table = sql_create_channel_cogs.read()
            create_admins_table = sql_create_admins.read()
            insert_cog = sql_insert_cog.read()

        db_path = os.environ["BOT_DB"]
        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        try:
            cursor.execute(create_users_table)
            cursor.execute(create_channels_table)
            cursor.execute(create_commands_table)
            cursor.execute(create_user_commands_table)
            cursor.execute(create_channel_commands_table)
            cursor.execute(create_cogs_table)
            cursor.execute(create_user_cogs_table)
            cursor.execute(create_channel_cogs_table)
            cursor.execute(create_admins_table)
            cursor.execute(insert_cog, (self.qualified_name,))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            raise

        db.commit()
        db.close()

    async def get_users(self) -> Tuple[int, ...]:
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        with (
            open(f"{sql_dir}/select_user_cogs.sql", "r")
                as sql_select_user_cogs,
        ):
            fetch_users = sql_select_user_cogs.read()

        db_path = os.environ["BOT_DB"]
        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        try:
            cursor.execute(fetch_users, (self.qualified_name,))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            raise

        user_records = cursor.fetchall()
        def pull_singleton(x): return x[0]
        users = tuple(map(pull_singleton, user_records))
        db.close()
        return users

    async def get_channels(self) -> Tuple[int, ...]:
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        with (
            open(f"{sql_dir}/select_channel_cogs.sql", "r")
                as sql_select_channel_cogs,
        ):
            fetch_channels = sql_select_channel_cogs.read()

        db_path = os.environ["BOT_DB"]
        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        try:
            cursor.execute(fetch_channels, (self.qualified_name,))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            raise

        channel_records = cursor.fetchall()
        def pull_singleton(x): return x[0]
        channels = tuple(map(pull_singleton, channel_records))
        db.close()
        return channels

    @staticmethod
    async def get_command_users(command_name: str) -> Tuple[int, ...]:
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        with (
            open(f"{sql_dir}/select_command_users.sql", "r")
                as sql_select_command_users,
        ):
            fetch_users = sql_select_command_users.read()

        db_path = os.environ["BOT_DB"]
        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        try:
            cursor.execute(fetch_users, (command_name,))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            raise

        user_records = cursor.fetchall()
        def pull_singleton(x): return x[0]
        users = tuple(map(pull_singleton, user_records))
        db.close()
        return users

    @staticmethod
    async def get_command_channels(command_name: str) -> Tuple[int, ...]:
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        with (
            open(f"{sql_dir}/select_command_channels.sql", "r")
                as sql_select_command_channels,
        ):
            fetch_channels = sql_select_command_channels.read()

        db_path = os.environ["BOT_DB"]
        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        try:
            cursor.execute(fetch_channels, (command_name,))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            raise

        channel_records = cursor.fetchall()
        def pull_singleton(x): return x[0]
        channels = tuple(map(pull_singleton, channel_records))
        db.close()
        return channels

    @staticmethod
    async def get_admins() -> Tuple[int, ...]:
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        with (
            open(f"{sql_dir}/select_admins_table.sql", "r")
                as sql_select_admins_table
        ):
            fetch_admins = sql_select_admins_table.read()

        db_path = os.environ["BOT_DB"]
        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        try:
            cursor.execute(fetch_admins)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            raise

        admin_records = cursor.fetchall()
        def pull_singleton(x): return x[0]
        admins = tuple(map(pull_singleton, admin_records))
        db.close()
        return admins

    async def cog_check(self, ctx: commands.Context) -> bool:
        permission: bool
        config = Config.from_json(os.environ["BOT_CONFIG"])
        if isinstance(ctx.channel, discord.channel.DMChannel):
            users = await self.get_command_users(ctx.command.qualified_name)
            admins = await self.get_admins()
            return (config.settings.enable_user_commands and
                    ((ctx.author.id in users) or (ctx.author.id in admins)))
        else:
            channels = (
                await self.get_command_channels(ctx.command.qualified_name)
            )
            return (config.settings.enable_channel_commands and
                    (ctx.channel.id in channels))

    async def cog_command_error(
            self,
            ctx: commands.Context,
            error: commands.CommandError
    ) -> None:
        match error:
            case commands.CommandOnCooldown():
                time = round(error.retry_after)
                await ctx.send(f"Command on cooldown for {time} seconds.")
            case commands.CheckFailure():
                pass
            case _:
                print(error)
                await ctx.send(f"Miscellaneous error. Please check logs.")
                config = Config.from_json(os.environ["BOT_CONFIG"])
                errors_log = config.logs.errors
                log = ('[' + str(datetime.now()) + ']' + " " +
                       traceback.format_exc())
                with open(errors_log, "a") as file:
                    print(log, file=file)

    async def create_webhook(
            self,
            channel: discord.TextChannel
    ) -> discord.Webhook:
        if (not await channel.webhooks()):
            icon = os.environ["BOT_ICON"]
            with open(icon, "rb") as image:
                img = image.read()
                img_b = bytearray(img)
                webhook = await channel.create_webhook(
                    name=f"{channel.name}-webhook",
                    avatar=img_b
                )

            print(f"Created webhook {channel.name}-webhook with URL",
                  webhook.url)

        config = Config.from_json(os.environ["BOT_CONFIG"])
        webhook_dir = (f"{config.dir.webhooks}/{self.qualified_name}")
        if (not os.path.exists(webhook_dir)):
            os.makedirs(webhook_dir)

        webhooks = await channel.webhooks()
        webhook = webhooks[0]
        with (
            open(
                webhook_dir + f"/{channel.name}-webhook.url",
                "w+"
            ) as file,
        ):
            print(webhook.url, file=file)

        return webhook

    def register_commands(self) -> None:
        command_names: List[Tuple[str, str]] = []
        for command in self.walk_commands():
            command_names.append((command.qualified_name, self.qualified_name))

        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        with (
            open(f"{sql_dir}/insert_command.sql", "r")
                as sql_insert_command,
        ):
            insert_command = sql_insert_command.read()

        db_path = os.environ["BOT_DB"]
        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        try:
            cursor.executemany(insert_command, command_names)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            raise

        db.commit()

    async def create_webhooks(self) -> None:
        for channel_id in await self.get_channels():
            channel = await self.bot.fetch_channel(channel_id)
            await self.create_webhook(channel)

    async def cog_load(self) -> None:
        self.register_commands()
        await self.create_webhooks()
        try:
            await self.bot.load_extension("cogs._db-base")
        except commands.ExtensionAlreadyLoaded:
            pass

        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        BaseCog.instances += 1
        print(eval(constants.messages.loaded_cog))

    async def cog_unload(self) -> None:
        BaseCog.instances -= 1
        if (BaseCog.instances == 0):
            await self.bot.unload_extension("cogs._db-base")

        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        print(eval(constants.messages.unloaded_cog))
