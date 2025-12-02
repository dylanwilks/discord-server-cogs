import os
import sys
import sqlite3
import discord
import asyncio
import dotenv
from typing import Tuple, List
from discord.ext import commands, tasks
from lib.config import Config

dotenv.load_dotenv()

async def admin(user_id: int):
    config = Config.from_json(os.environ["BOT_CONFIG"])
    sql_dir = config.dir.sql
    with (
        open(f"{sql_dir}/insert_admin.sql", "r")
            as sql_insert_admin,
    ):
        set_admin = sql_insert_admin.read()

    db_path = os.environ["BOT_DB"]
    db = sqlite3.connect(db_path, check_same_thread=False)
    db.execute("PRAGMA FOREIGN_KEYS = ON")
    cursor = db.cursor()
    cursor.execute(set_admin, (user_id,))
    db.commit()
    db.close()

if __name__ == "__main__":
    asyncio.run(admin(sys.argv[1]))
