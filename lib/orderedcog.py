import os
import sys
import sqlite3
import discord
from typing import Callable, Optional
from discord.ext import commands
from basecog import BaseCog
from alerts import Alerts


class OrderedCog(BaseCog):
    instances = 0

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)
        with (
            open(
                "/root/discord-bot/db/scripts/create_user_perms.sql",
                "r",
            ) as sql_create_user_perms,
            open(
                "/root/discord-bot/db/scripts/create_channel_perms.sql",
                "r",
            ) as sql_create_channel_perms,
        ):
            create_user_perms_table = sql_create_user_perms.read()
            create_channel_perms_table = sql_create_channel_perms.read()

        db = sqlite3.connect(
            "/root/discord-bot/db/alpine-bot.db",
            check_same_thread=False
        )
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        try:
            cursor.execute(create_user_perms_table)
            cursor.execute(create_channel_perms_table)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

        db.commit()
        db.close()

    async def get_user_perm(self, user_id: int) -> Optional[int]:
        with (
            open("/root/discord-bot/db/scripts/select_user_perm.sql", "r")
                as sql_select_user_perm,
        ):
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
        with (
            open("/root/discord-bot/db/scripts/select_channel_perm.sql", "r")
                as sql_select_channel_perm,
        ):
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

    class PermissionError(commands.CommandError):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    @staticmethod
    def assert_perms(
            user_perm: int,
            channel_perm: int
    ) -> Callable[[commands.Context], bool]:
        assert user_perm >= channel_perm

        async def predicate(ctx: commands.Context) -> bool:
            cog = ctx.cog
            admins = await cog.get_admins()
            if (ctx.author.id in admins):
                return True

            cog_user_perm = await cog.get_user_perm(ctx.author.id)
            cog_channel_perm = await cog.get_channel_perm(ctx.channel.id)
            permission: bool
            if (cog_user_perm is not None):
                permission = cog_user_perm >= user_perm
            else:
                permission = cog_channel_perm >= channel_perm

            if (permission):
                return True
            else:
                raise OrderedCog.PermissionError(
                    f"""
                    Mismtaching permissions (KEY user_perm:channel_perm):
                    Required: {user_perm}:{channel_perm}
                    Actual: {cog_user_perm}:{cog_channel_perm}
                    """
                )

        return commands.check(predicate)

    async def cog_command_error(
            self,
            ctx: commands.Context,
            error: commands.CommandError
    ) -> None:
        match error:
            case self.PermissionError():
                await ctx.send(Alerts.NO_COMMAND_PERM)
            case _:
                await super().cog_command_error(ctx, error)

    async def cog_load(self) -> None:
        await super().cog_load()
        try:
            await self.bot.load_extension("cogs._db-ordered")
        except commands.ExtensionAlreadyLoaded:
            pass

        OrderedCog.instances += 1

    async def cog_unload(self) -> None:
        OrderedCog.instances -= 1
        if (OrderedCog.instances == 0):
            await self.bot.unload_extension("cogs._db-ordered")

        await super().cog_unload()
