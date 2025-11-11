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
from typing import Any, Tuple, Mapping
from datetime import datetime
from discord.ext import commands, tasks
sys.path.append('cogs')
sys.path.append('cogs/servers')
sys.path.append('lib')
from alerts import Alerts

handler = logging.FileHandler(
    filename='/var/log/discord/alpine-bot.log',
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
            **kwargs: Mapping[str, Any]
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
            await asyncio.sleep(5)

    async def on_error(
            self,
            event_method: str,
            *args: Tuple[Any, ...],
            **kwargs: Mapping[str, Any]
    ) -> None:
        self.logger.error(f"An error occured in {event_method}!\n"
                          f"{traceback.format_exc()}.")

    async def on_ready(self) -> None:
        if self.user.name != 'Alpine Bot':
            await self.user.edit(username='Alpine Bot')

        print(f'Logged in as {self.user}.')
        self.check_name.start()
        with (
            open("/root/discord-bot/db/scripts/select_users_table.sql", "r")
                as sql_select_users_table,
            open("/root/discord-bot/db/scripts/select_channels_table.sql", "r")
                as sql_select_channels_table,
        ):
            get_users_table = sql_select_users_table.read()
            get_channels_table = sql_select_channels_table.read()

        db = sqlite3.connect(
            "/root/discord-bot/db/alpine-bot.db",
            check_same_thread=False
        )
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_users_table)
        user_records = cursor.fetchall()
        cursor.execute(get_channels_table)
        channel_records = cursor.fetchall()
        db.close()
        for record in user_records:
            user = await self.fetch_user(record[0])
            user_dm = await user.create_dm()
            await user_dm.send(Alerts.STARTUP)

        for record in channel_records:
            channel = await self.fetch_channel(record[0])
            await channel.send(Alerts.STARTUP)

    async def on_command_completion(self, ctx: commands.Context) -> None:
        log = ('[' + str(datetime.now()) + ']' + " " + ctx.author.name +
               " issued_command " + ctx.message.content + " in ")
        if isinstance(ctx.channel, discord.channel.DMChannel):
            log += "private DMs."
        else:
            log += "#" + ctx.channel.name + "."

        print(log)
        with open("/var/log/discord/commands.log", "a") as file:
            print(log, file=file)

    async def setup_hook(self) -> None:
        await self._load_extensions()
        self._watcher = self.loop.create_task(self._cog_watcher())

    @tasks.loop(minutes=10.0)
    async def check_name(self) -> None:
        if (self.user.name != 'Alpine Bot'):
            await self.user.edit(username='Alpine Bot')


bot = AlpineBot("cogs", command_prefix="!", intents=intents)
bot.run(
    'MTM5MzAyMDkxMTE5NTc4NzM2Ng.GCUoCr.BvhTfnsKRzT7gkBBgxVoUbFEHNK63LxhlbF068',
    log_handler=handler,
    log_level=logging.DEBUG
)
