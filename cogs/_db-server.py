import sqlite3
import discord
from discord.ext import tasks, commands
from alerts import Alerts
from basecog import BaseCog
from servercog import ServerCog


class ServerCogDatabase(
        BaseCog,
        name="db-server",
        description="Commands for the database relating to ServerCog."
):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.db_cog = self.bot.get_cog("db-base")

    @commands.command(
        name="print-servers-table",
        brief="Prints all records of the Servers table.",
        help="""
            Displays records within the Servers table as tuples. Automatically
            changes state flag into corresponding enum name.
            """
    )
    async def print_servers_table(self, ctx: commands.Context) -> None:
        await ctx.send(f"Fetching Servers table...")
        with (
            open("/root/discord-bot/db/scripts/select_servers_table.sql", "r")
                as sql_select_servers_table,
        ):
            get_server_records = sql_select_servers_table.read()

        db = sqlite3.connect(
            "/root/discord-bot/db/alpine-bot.db",
            check_same_thread=False
        )
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_server_records)
        server_records = cursor.fetchall()
        db.close()
        message = ""
        for record in server_records:
            m_record = list(record)
            server_cog = self.bot.get_cog(record[0])
            m_record[1] = server_cog.State(record[1]).name
            new_row = str(tuple(m_record)) + '\n'
            if (len(message) + len(new_row) > 2000):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @commands.command(
        name="delete-server",
        brief="Removes a server.",
        help="""
            Removes the given server from the database. This will also remove the
            cog.
            """
    )
    async def delete_server(
            self,
            ctx: commands.Context,
            server_name: str = commands.parameter(
                description="Name of the server"
            )
    ) -> None:
        server_cog = self.bot.get_cog(server_name)
        if (server_cog is None or
                not issubclass(type(server_cog), ServerCog)):
            await ctx.send("Invalid cog name.")
            return

        await ctx.send(f"Removing server {server_name}...")
        await self.bot.remove_cog(server_name)
        with (
            open("/root/discord-bot/db/scripts/delete_server.sql", "r")
                as sql_delete_server,
        ):
            delete_server_record = sql_delete_server.read()

        db = sqlite3.connect(
            "/root/discord-bot/db/alpine-bot.db",
            check_same_thread=False
        )
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(delete_server_record, (server_name,))
        db.commit()
        db.close()
        await ctx.send("Database successfully updated.")

    async def cog_load(self) -> None:
        for command in self.walk_commands():
            command_copy = command.copy()
            command_copy.enabled = True
            command_copy.cog = self.db_cog
            try:
                self.db_cog.db_group.add_command(command_copy)
            except commands.CommandRegistrationError:
                pass

            command.enabled = False

        self.db_cog.register_commands()
        await self.db_cog.create_webhooks()
        print(f"Loaded cog {self.qualified_name}.")

    async def cog_unload(self) -> None:
        for command in self.walk_commands():
            self.db_cog.db_group.remove_command(command.name)

        print(f"Unloaded cog {self.qualified_name}.")


async def setup(bot) -> None:
    await bot.add_cog(ServerCogDatabase(bot))
