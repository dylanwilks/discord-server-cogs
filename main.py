import os
import sys
import time
import pathlib
import asyncio
import logging
import discord
import typing
import traceback
import sqlite3
import dotenv
from typing import Any, Tuple, Mapping, Dict
from datetime import datetime
from discord.ext import commands, tasks
from lib.config import Config

dotenv.load_dotenv()
config = Config.from_json(os.environ["BOT_CONFIG"])
constants = Config.from_json(os.environ["BOT_CONSTANTS"])
handler = logging.FileHandler(
    filename=config.logs.handler,
    encoding='utf-8',
    mode='w'
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


# Number of features here taken from fallendeity
class AlpineBot(commands.Bot):
    _watcher: asyncio.Task

    def __init__(
            self,
            ext_dir: str,
            *args: Tuple[Any, ...],
            **kwargs: Dict[str, Any]
    ) -> None:
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ext_dir = pathlib.Path(ext_dir)

    async def _load_extensions(self) -> None:
        print("Loading extensions...")
        for file in self.ext_dir.rglob("*.py"):
            if (file.stem.startswith("_")):
                continue

            try:
                await self.load_extension(".".join(file.with_suffix("").parts))
                print(f"Loaded extension {file}")
            except commands.ExtensionError as e:
                print(f"Failed to load extension {file}: {e}")
                log = ('[' + str(datetime.now()) + ']' + " " + 
                       traceback.format_exc())
                with open(config.logs.errors, "a") as file:
                    print(log, file=file)

    async def _cog_watcher(self) -> None:
        print("Watching for changes...")
        last = time.time()
        while True:
            extensions: set[str] = set()
            for name, module in self.extensions.items():
                try:
                    if (module.__file__ and
                            os.stat(module.__file__).st_mtime > last):
                        extensions.add(name)
                except FileNotFoundError as e:
                    print(f"Failed to find module {module.__file__}: {e}")
                    continue

            for ext in extensions:
                try:
                    await self.reload_extension(ext)
                    print(f"Reloaded extension {ext}")
                except commands.ExtensionError as e:
                    print(f"Failed to reload extension {ext}: {e}")

            last = time.time()
            sleep_time = float(os.getenv("BOT_WATCHER_SECONDS", 1))
            await asyncio.sleep(sleep_time)

    async def on_error(
            self,
            event_method: str,
            *args: Tuple[Any, ...],
            **kwargs: Mapping[str, Any]
    ) -> None:
        self.logger.error(f"An error occured in {event_method}!\n"
                          f"{traceback.format_exc()}.")

    async def on_ready(self) -> None:
        bot_name = os.getenv("BOT_NAME", "")
        if (bot_name != "" and self.user.name != bot_name):
            await self.user.edit(username=bot_name)
        
        bot_icon = os.getenv("BOT_ICON", "")
        if (bot_icon != ""):
            with open(bot_icon, 'rb') as image:
                await self.user.edit(avatar=image.read())

        print(f'Logged in as {self.user}.')
        self.check_name.start()
        sql_dir = config.dir.sql
        with (
            open(f"{sql_dir}/select_users_table.sql", "r")
                as sql_select_users_table,
            open(f"{sql_dir}/select_channels_table.sql", "r")
                as sql_select_channels_table,
        ):
            get_users_table = sql_select_users_table.read()
            get_channels_table = sql_select_channels_table.read()
        
        db_path = os.environ["BOT_DB"]
        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_users_table)
        user_records = cursor.fetchall()
        cursor.execute(get_channels_table)
        channel_records = cursor.fetchall()
        db.close()
        enable_start_message = config.settings.enable_start_message
        if (enable_start_message):
            msg_startup = eval(constants.messages.startup)
            for record in user_records:
                user = await self.fetch_user(record[0])
                user_dm = await user.create_dm()
                await user_dm.send(msg_startup)

            for record in channel_records:
                channel = await self.fetch_channel(record[0])
                await channel.send(msg_startup)

    async def on_command(self, ctx: commands.Context) -> None:
        log = ('[' + str(datetime.now()) + ']' + " " + ctx.author.name +
               " issued_command " + ctx.message.content + " in ")
        if isinstance(ctx.channel, discord.channel.DMChannel):
            log += "private DMs."
        else:
            log += "#" + ctx.channel.name + "."

        print(log)
        with open(config.logs.commands, "a") as file:
            print(log, file=file)

    async def setup_hook(self) -> None:
        await self._load_extensions()
        self._watcher = self.loop.create_task(self._cog_watcher())

    @tasks.loop(minutes=float(os.getenv("BOT_NAME_MINUTES", 10.0)))
    async def check_name(self) -> None:
        bot_name = os.getenv("BOT_NAME", "")
        if (bot_name != "" and self.user.name != bot_name):
            await self.user.edit(username=bot_name)


command_prefix = os.environ["BOT_PREFIX"]
bot = AlpineBot(config.dir.cogs, command_prefix=command_prefix, intents=intents)
bot_token = os.environ["BOT_TOKEN"]
bot.run(
    bot_token,
    log_handler=handler,
    log_level=logging.DEBUG
)
