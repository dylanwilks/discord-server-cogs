import sys
import sqlite3
import discord
import asyncio
from typing import Tuple, List
from discord.ext import commands, tasks


async def admin(user_id: int):
    with (
        open("/root/discord-bot/db/scripts/insert_admin.sql", "r")
            as sql_insert_admin,
    ):
        set_admin = sql_insert_admin.read()

    db = sqlite3.connect(
        "/root/discord-bot/db/alpine-bot.db",
        check_same_thread=False
    )
    db.execute("PRAGMA FOREIGN_KEYS = ON")
    cursor = db.cursor()
    cursor.execute(set_admin, (user_id,))
    db.commit()
    db.close()

if __name__ == "__main__":
    asyncio.run(admin(sys.argv[1]))
