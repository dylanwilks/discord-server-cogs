import os
import sys
import sqlite3
import discord
from enum import IntFlag
from typing import Callable
from discord.ext import commands
from orderedcog import OrderedCog


class ServerCog(OrderedCog):
    instances = 0

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)
        if (not issubclass(self.State, IntFlag)):
            raise NotImplementedError("State not a subclass of IntFlag")

        try:
            self.State.ACTIVE
            self.State.INACTIVE
        except AttributeError as e:
            raise NotImplementedError(f"No state {e} detected")

        with (
            open(
                "/root/discord-bot/db/scripts/create_servers.sql",
                "r",
            ) as sql_create_server,
            open(
                "/root/discord-bot/db/scripts/insert_server.sql",
                "r",
            ) as sql_insert_server,
        ):
            create_servers_table = sql_create_server.read()
            insert_server = sql_insert_server.read()

        db = sqlite3.connect(
            "/root/discord-bot/db/alpine-bot.db",
            check_same_thread=False
        )
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        try:
            cursor.execute(create_servers_table)
            cursor.execute(
                insert_server,
                (self.qualified_name, self.State.INACTIVE.value)
            )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

        db.commit()
        db.close()

    async def _update_state(self, state: 'State') -> None:
        with (
            open("/root/discord-bot/db/scripts/update_server_state.sql", "r")
                as sql_update_server_state,
        ):
            update_server = sql_update_server_state.read()

        db = sqlite3.connect(
            "/root/discord-bot/db/alpine-bot.db",
            check_same_thread=False
        )
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(
            update_server,
            (state.value, self.qualified_name)
        )
        db.commit()
        db.close()

    async def get_state(self) -> 'State':
        with (
            open("/root/discord-bot/db/scripts/select_server_state.sql", "r")
                as sql_select_server_state,
        ):
            get_state = sql_select_server_state.read()

        db = sqlite3.connect(
            "/root/discord-bot/db/alpine-bot.db",
            check_same_thread=False
        )
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_state, (self.qualified_name,))
        state = self.State(cursor.fetchone()[0])
        db.close()
        return state

    class ServerError(commands.CommandError):
        def __init__(self, message: str, server: str) -> None:
            self.message = message
            self.server = server 
            super().__init__(self.message)

    class StateError(commands.CommandError):
        def __init__(self, message: str, state: 'State') -> None:
            self.message = message
            self.state = state
            super().__init__(self.message)

    @staticmethod
    def assert_state(state: 'State') -> Callable[[commands.Context], bool]:
        async def predicate(ctx: commands.Context) -> bool:
            server_cog = ctx.cog
            server_state = await server_cog.get_state()
            if (server_state & state):
                return True
            else:
                raise ServerCog.StateError(
                    f"""
                    Mismatching states:
                    Required: {state.name}
                    Actual: {server_state}
                    """,
                    server_state
                )

        return commands.check(predicate)

    async def cog_command_error(
            self,
            ctx: commands.Context,
            error: commands.CommandError
    ) -> None:
        match error:
            case self.StateError():
                await ctx.send(f"Command unavailable in current state: "
                               f"{error.state.name}")
            case self.ServerError():
                await ctx.send(error.message)
            case _:
                await super().cog_command_error(ctx, error)

    async def cog_load(self) -> None:
        await super().cog_load()
        try:
            await self.bot.load_extension("cogs._db-server")
        except commands.ExtensionAlreadyLoaded:
            pass

        ServerCog.instances += 1

    async def cog_unload(self) -> None:
        ServerCog.instances -= 1
        if (ServerCog.instances == 0):
            await self.bot.unload_extension("cogs._db-server")

        await super().cog_unload()
