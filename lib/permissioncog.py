import sqlite3
import discord
from typing import Tuple, List
from discord.ext import commands, tasks
from commandscog import CommandsCog


class PermissionCog(BaseCog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)
        with
        open("/root/discord-bot/db/scripts/create_shared_cogs.sql",
             "r",
             ) as sql_create_shared_cogs,
        open("/root/discord-bot/db/scripts/create_user_perms.sql",
             "r",
             ) as sql_create_user_perms,
        open("/root/discord-bot/db/scripts/create_channel_perms.sql",
             "r",
             ) as sql_create_channel_perms,
        open("/root/discord-bot/db/scripts/insert_shared_cog.sql",
             "r",
             ) as sql_insert_shared_cog
        :
            create_shared_cogs_table = sql_create_shared_cogs.read()
            create_user_perms_table = sql_create_user_perms.read()
            create_channel_perms_tablwe = sql_create_channel_perms.read()
            insert_shared_cog = sql_insert_shared_cog.read()

        db = sqlite3.connect(
            "/root/discord-bot/db/alpine-bot.db",
            check_same_thread=False
        )
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(create_shared_cogs_table)
        cursor.execute(create_user_perms_table)
        cursor.execute(create_channel_perms_table)
        cursor.execute(insert_shared_cog, (self.qualified_name,))
        db.close()

    async def get_user_perm(self, user_id: int) -> Optional[int]:
        with open("/root/discord-bot/db/scripts/select_user_perm.sql", "r")
        as sql_select_user_perm:
            fetch_user_perm = sql_select_user_perm.read()

        db = sqlite3.connect(
            "/root/discord-bot/db/alpine-bot.db",
            check_same_thread=False
        )
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(
            fetch_user_perm,
            (user_id, self.qualified_name)
        )
        user_perm = cursor.fetchone()
        db.close()
        if (user_perm is None):
            return user_perm
        else:
            return user_perm[0]

    async def get_channel_perm(self, channel_id: int) -> Optional[int]:
        with open("/root/discord-bot/db/scripts/select_channel_perm.sql", "r")
        as sql_select_channel_perm:
            fetch_channel_perm = sql_select_channel_perm.read()

        db = sqlite3.connect(
            "/root/discord-bot/db/alpine-bot.db",
            check_same_thread=False
        )
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(
            fetch_channel_perm,
            (channel_id, self.qualified_name)
        )
        channel_perm = cursor.fetchone()
        db.close()
        if (channel_perm is None):
            return channel_perm
        else:
            return channel_perm[0]
