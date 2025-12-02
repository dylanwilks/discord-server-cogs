import os
import sqlite3
import discord
from discord.ext import commands
from typing import List, Tuple, Final
from lib.basecog import BaseCog
from lib.config import Config

DB_COOLDOWN: Final[float] = 5.0


class BaseCogDatabase(
        BaseCog,
        name="db-base",
        description="Commands for the database relating to BaseCog."
):
    @commands.group(
        name="db",
        invoke_without_command=True,
        brief="Group of commands for accessing the database.",
        help="""
            Group composing of commands that fetch and update
            database records.
            """
    )
    @commands.cooldown(1, DB_COOLDOWN)
    async def db_group(self, ctx: commands.Context) -> None:
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await ctx.send(eval(constants.messages.servers.no_subcommand))

    @db_group.command(
        name="print-users-table",
        brief="Prints all records of the Users table.",
        help="""
            Displays records within the Users table as tuples.
            Automatically converts user IDs into usernames.
            """
    )
    async def print_users_table(
            self,
            ctx: commands.Context
    ) -> None:
        await ctx.send(f"Fetching Users table...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_users_table.sql", "r")
                as sql_select_users_table
        ):
            get_user_records = sql_select_users_table.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_user_records)
        user_records = cursor.fetchall()
        db.close()
        message = ""
        message_limit = int(config.settings.message_limit)
        for record in user_records:
            user = await self.bot.fetch_user(record[0])
            new_row = user.name + ' ' + str(record) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @db_group.command(
        name="print-channels-table",
        brief="Prints all records of the Channels table.",
        help="""
            Displays records within the Channels table as tuples.
            Automatically converts channel IDs into channel names.
            """
    )
    async def print_channels_table(
            self,
            ctx: commands.Context
    ) -> None:
        await ctx.send(f"Fetching Channels table...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_channels_table.sql", "r")
                as sql_select_channels_table,
        ):
            get_channel_records = sql_select_channels_table.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_channel_records)
        channel_records = cursor.fetchall()
        db.close()
        message = ""
        message_limit = config.settings.message_limit
        for record in channel_records:
            channel = await self.bot.fetch_channel(record[0])
            new_row = '#' + channel.name + ' ' + str(record) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @db_group.command(
        name="print-commands-table",
        brief="Prints all records of the Commands table.",
        help="""
            Displays records within the Commands table as tuples.
            """
    )
    async def print_commands_table(
            self,
            ctx: commands.Context
    ) -> None:
        await ctx.send(f"Fetching Commands table...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_commands_table.sql", "r")
                as sql_select_commands_table,
        ):
            get_commands_records = sql_select_commands_table.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_commands_records)
        commands_records = cursor.fetchall()
        db.close()
        message = ""
        message_limit = config.settings.message_limit
        for record in commands_records:
            new_row = str(record) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @db_group.command(
        name="print-cogs-table",
        brief="Prints all records of the Cogs table.",
        help="""
            Displays records within the Cogs table as tuples.
            """
    )
    async def print_cogs_table(
            self,
            ctx: commands.Context
    ) -> None:
        await ctx.send(f"Fetching Cogs table...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_cogs_table.sql", "r")
                as sql_select_cogs_table,
        ):
            get_cogs_records = sql_select_cogs_table.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_cogs_records)
        cogs_records = cursor.fetchall()
        db.close()
        message = ""
        message_limit = config.settings.message_limit
        for record in cogs_records:
            new_row = str(record) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @db_group.command(
        name="print-user-cogs-table",
        brief="Prints all records of the UserCogs table.",
        help="""
            Displays records within the UserCogs table as tuples.
            Automatically converts user IDs into usernames.
            """
    )
    async def print_user_cogs_table(
            self,
            ctx: commands.Context
    ) -> None:
        await ctx.send(f"Fetching UserCogs table...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_user_cogs_table.sql", "r")
                as sql_select_user_cogs_table,
        ):
            get_user_cogs_records = sql_select_user_cogs_table.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_user_cogs_records)
        user_cogs_records = cursor.fetchall()
        db.close()
        message = ""
        message_limit = config.settings.message_limit
        for record in user_cogs_records:
            m_record = list(record)
            user = await self.bot.fetch_user(record[0])
            m_record[0] = user.name
            new_row = str(tuple(m_record)) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @db_group.command(
        name="print-channel-cogs-table",
        brief="Prints all records of the ChannelCogs table.",
        help="""
            Displays records within the ChannelCogs table as tuples.
            Automatically converts channel IDs into channelnames.
            """
    )
    async def print_channel_cogs_table(
            self,
            ctx: commands.Context
    ) -> None:
        await ctx.send(f"Fetching ChannelCogs table...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_channel_cogs_table.sql", "r")
                as sql_select_channel_cogs_table,
        ):
            get_channel_cogs_records = sql_select_channel_cogs_table.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_channel_cogs_records)
        channel_cogs_records = cursor.fetchall()
        db.close()
        message = ""
        message_limit = config.settings.message_limit
        for record in channel_cogs_records:
            m_record = list(record)
            channel = await self.bot.fetch_channel(record[0])
            m_record[0] = "#" + channel.name
            new_row = str(tuple(m_record)) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @db_group.command(
        name="print-user-commands-table",
        brief="Prints all records of the UserCommands table.",
        help="""
            Displays records within the UserCommands table as tuples.
            Automatically converts user IDs into usernames.
            """
    )
    async def print_user_commands_table(
            self,
            ctx: commands.Context
    ) -> None:
        await ctx.send(f"Fetching UserCommands table...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_user_commands_table.sql", "r")
                as sql_select_user_commands_table,
        ):
            get_user_commands_records = sql_select_user_commands_table.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_user_commands_records)
        user_command_records = cursor.fetchall()
        db.close()
        message = ""
        message_limit = config.settings.message_limit
        for record in user_command_records:
            m_record = list(record)
            user = await self.bot.fetch_user(record[0])
            m_record[0] = user.name
            new_row = str(tuple(m_record)) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @db_group.command(
        name="print-channel-commands-table",
        brief="Prints all records of the ChannelCommands table.",
        help="""
            Displays records within the ChannelCommands table as tuples.
            Automatically converts channel IDs into channel names.
            """
    )
    async def print_channel_commands_table(
            self,
            ctx: commands.Context
    ) -> None:
        await ctx.send(f"Fetching ChannelCommands table...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_channel_commands_table.sql", "r")
                as sql_select_channel_commands_table,
        ):
            get_channel_commands_records = (
                sql_select_channel_commands_table.read()
            )

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_channel_commands_records)
        channel_command_records = cursor.fetchall()
        db.close()
        message = ""
        message_limit = config.settings.message_limit
        for record in channel_command_records:
            m_record = list(record)
            channel = await self.bot.fetch_channel(record[0])
            m_record[0] = "#" + channel.name
            new_row = str(tuple(m_record)) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @db_group.command(
        name="print-command-users",
        brief="Prints records of users linked to the given command.",
        help="""
            Displays records from the UserCommands table with the given
            command name as foreign key. Automatically converts the user ID
            into the corresponding username.
            """
    )
    async def print_command_users(
            self,
            ctx: commands.Context,
            *,
            command_name: str = commands.parameter(
                description="Name of the command"
            )
    ) -> None:
        await ctx.send(f"Fetching UserCommands records "
                       f"linked to {command_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_command_user_records.sql", "r")
                as sql_select_command_user_records,
        ):
            get_command_users = sql_select_command_user_records.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_command_users, (command_name,))
        command_users = cursor.fetchall()
        db.close()
        message = ""
        message_limit = config.settings.message_limit
        for record in command_users:
            m_record = list(record)
            user = await self.bot.fetch_user(record[0])
            m_record[0] = user.name
            new_row = str(tuple(m_record)) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @db_group.command(
        name="print-command-channels",
        brief="Prints records of channels linked to the given command.",
        help="""
            Displays records from the ChannelCommands table with the given
            command name as foreign key. Automatically converts the channel ID
            into the corresponding username.
            """
    )
    async def print_command_channels(
            self,
            ctx: commands.Context,
            *,
            command_name: str = commands.parameter(
                description="Name of the command"
            )
    ) -> None:
        await ctx.send(f"Fetching ChannelCommands records "
                       f"linked to {command_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_command_channel_records.sql", "r")
                as sql_select_command_channel_records,
        ):
            get_command_channels = sql_select_command_channel_records.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(get_command_channels, (command_name,))
        command_channels = cursor.fetchall()
        db.close()
        message = ""
        message_limit = config.settings.message_limit
        for record in command_channels:
            m_record = list(record)
            channel = await self.bot.fetch_channel(record[0])
            m_record[0] = "#" + channel.name
            new_row = str(tuple(m_record)) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @db_group.command(
        name="permit-user-command",
        brief="Permits the user to use the given command.",
        help="""
            Permits the user to use the given command. If the user does
            not exist in the database, records will be generated.
            """
    )
    async def permit_user_command(
            self,
            ctx: commands.Context,
            user_id: int = commands.parameter(
                description="ID of the user"
            ),
            *,
            command_name: str = commands.parameter(
                description="Name of the command"
            )
    ) -> None:
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        try:
            user = await self.bot.fetch_user(user_id)
        except NotFound as e:
            await ctx.send(constants.messages.invalid_user)
            return

        command = self.bot.get_command(command_name)
        if (command is None):
            await ctx.send(constants.messages.invalid_channel)
            return

        await ctx.send(f"Permitting user {user.name} "
                       f"to use command {command_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/insert_user.sql", "r")
                as sql_insert_user,
            open(f"{sql_dir}/insert_user_command.sql", "r")
                as sql_insert_user_command,
            open(f"{sql_dir}/insert_user_cog.sql", "r")
                as sql_insert_user_cog,
        ):
            add_user = sql_insert_user.read()
            add_user_command = sql_insert_user_command.read()
            add_cog_user = sql_insert_user_cog.read()

        cog_name = command.cog.qualified_name
        user_commands: List[Tuple[int, str, str]] = []
        user_commands.append((user_id, command_name, cog_name))
        for parent in command.parents:
            user_commands.append((user_id, parent.qualified_name, cog_name))

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(add_user, (user_id,))
        if (cursor.rowcount):
            user_dm = await user.create_dm()
            await user_dm.send(eval(constants.messages.startup))

        cursor.executemany(add_user_command, user_commands)
        cursor.execute(add_cog_user, (user_id, cog_name))
        db.commit()
        db.close()
        await ctx.send(constants.messages.db_update)

    @db_group.command(
        name="permit-channel-command",
        brief="Permits the channel to use the given command.",
        help="""
            Permits the channel to use the given command. If the channel does
            not exist in the database, records will be generated.
            """
    )
    async def permit_channel_command(
            self,
            ctx: commands.Context,
            channel_id: int = commands.parameter(
                description="ID of the channel"
            ),
            *,
            command_name: str = commands.parameter(
                description="Name of the command"
            )
    ) -> None:
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        try:
            channel = await self.bot.fetch_channel(channel_id)
        except NotFound as e:
            await ctx.send(constants.messages.invalid_channel)
            return

        command = self.bot.get_command(command_name)
        if (command is None):
            await ctx.send(constants.messages.invalid_command)
            return

        await ctx.send(f"Permitting channel {channel.name} "
                       f"to use command {command_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/insert_channel.sql", "r")
                as sql_insert_channel,
            open(f"{sql_dir}/insert_channel_command.sql", "r")
                as sql_insert_channel_command,
            open(f"{sql_dir}/insert_channel_cog.sql", "r")
                as sql_insert_channel_cog,
        ):
            add_channel = sql_insert_channel.read()
            add_channel_command = sql_insert_channel_command.read()
            add_cog_channel = sql_insert_channel_cog.read()

        cog_name = command.cog.qualified_name
        channel_commands: List[Tuple[int, str, str]] = []
        channel_commands.append((channel_id, command_name, cog_name))
        for parent in command.parents:
            channel_commands.append(
                (channel_id, parent.qualified_name, cog_name))

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(add_channel, (channel_id,))
        if (cursor.rowcount):
            await self.create_webhook(channel)
            await channel.send(eval(constants.messages.startup))

        cursor.executemany(add_channel_command, channel_commands)
        cursor.execute(add_cog_channel, (channel_id, cog_name))
        db.commit()
        db.close()
        await ctx.send(constants.messages.db_update)

    @db_group.command(
        name="permit-user-cog",
        brief="Permits the user access to all commands in a cog.",
        help="""
            Permits the user to use all commands in a given cog. Cog must be
            a subclass of BaseCog. If the user does not exist in the database,
            records will be generated.
            """
    )
    async def permit_user_cog(
            self,
            ctx: commands.Context,
            user_id: int = commands.parameter(
                description="ID of the user"
            ),
            cog_name: str = commands.parameter(
                description="Name of the cog"
            )
    ) -> None:
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        try:
            user = await self.bot.fetch_user(user_id)
        except NotFound as e:
            await ctx.send(constants.messages.invalid_user)
            return

        cog = self.bot.get_cog(cog_name)
        if (cog is None or
                not issubclass(type(cog), BaseCog)):
            await ctx.send(constants.messages.invalid_cog)
            return

        await ctx.send(f"Permitting user {user.name} to use commands in cog "
                       f"{cog_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/insert_user.sql", "r")
                as sql_insert_user,
            open(f"{sql_dir}/insert_user_command.sql", "r")
                as sql_insert_user_command,
            open(f"{sql_dir}/insert_user_cog.sql", "r")
                as sql_insert_user_cog,
        ):
            add_user = sql_insert_user.read()
            add_user_command = sql_insert_user_command.read()
            add_cog_user = sql_insert_user_cog.read()

        user_commands: List[Tuple[int, str, str]] = []
        for command in cog.walk_commands():
            user_commands.append((user_id, command.qualified_name, cog_name))
            for parent in command.parents:
                user_commands.append(
                    (user_id, parent.qualified_name, cog_name))

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(add_user, (user_id,))
        if (cursor.rowcount):
            user_dm = await user.create_dm()
            await user_dm.send(eval(constants.messages.startup))

        cursor.executemany(add_user_command, user_commands)
        cursor.execute(add_cog_user, (user_id, cog_name))
        db.commit()
        db.close()
        await ctx.send(constants.messages.db_update)

    @db_group.command(
        name="permit-channel-cog",
        brief="Permits the channel access to all commands in a cog.",
        help="""
            Permits the channel to use all commands in a given cog. Cog must be
            a subclass of BaseCog. If the channel does not exist in the database,
            records will be generated.
            """
    )
    async def permit_channel_cog(
            self,
            ctx: commands.Context,
            channel_id: int = commands.parameter(
                description="ID of the channel"
            ),
            cog_name: str = commands.parameter(
                description="Name of the cog"
            )
    ) -> None:
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        try:
            channel = await self.bot.fetch_channel(channel_id)
        except NotFound as e:
            await ctx.send(constants.messages.invalid_channel)
            return

        cog = self.bot.get_cog(cog_name)
        if (cog is None or
                not issubclass(type(cog), BaseCog)):
            await ctx.send(constants.messages.invalid_cog)
            return

        await ctx.send(f"Permitting channel {channel.name} to use commands in "
                       f"cog {cog_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/insert_channel.sql", "r")
                as sql_insert_channel,
            open(f"{sql_dir}/insert_channel_command.sql", "r")
                as sql_insert_channel_command,
            open(f"{sql_dir}/insert_channel_cog.sql", "r")
                as sql_insert_channel_cog,
        ):
            add_channel = sql_insert_channel.read()
            add_channel_command = sql_insert_channel_command.read()
            add_cog_channel = sql_insert_channel_cog.read()

        channel_commands: List[Tuple[int, str, str]] = []
        for command in cog.walk_commands():
            channel_commands.append(
                (channel_id, command.qualified_name, cog_name))
            for parent in command.parents:
                channel_commands.append(
                    (channel_id, parent.qualified_name, cog_name))

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(add_channel, (channel_id,))
        if (cursor.rowcount):
            await self.create_webhook(channel)
            await channel.send(eval(constants.messages.startup))

        cursor.executemany(add_channel_command, channel_commands)
        cursor.execute(add_cog_channel, (channel_id, cog_name))
        db.commit()
        db.close()
        await ctx.send(constants.messages.db_update)

    @db_group.command(
        name="delete-user",
        brief="Removes a user.",
        help="""
            Removes the given user from the entire database.
            """
    )
    async def delete_user(
            self,
            ctx: commands.Context,
            user_id: int = commands.parameter(
                description="ID of the user"
            )
    ) -> None:
        user = await self.bot.fetch_user(user_id)
        username = user.name
        await ctx.send(f"Deleting user {username} from database...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/delete_user.sql", "r")
                as sql_delete_user,
        ):
            delete_user = sql_delete_user.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(delete_user, (user_id,))
        db.commit()
        db.close()
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await ctx.send(constants.messages.db_update)

    @db_group.command(
        name="delete-channel",
        brief="Removes a channel.",
        help="""
            Removes the given channel from the entire database.
            """
    )
    async def delete_channel(
            self,
            ctx: commands.Context,
            channel_id: int = commands.parameter(
                description="ID of the channel"
            )
    ) -> None:
        channel = await self.bot.fetch_channel(channel_id)
        webhooks = await channel.webhooks()
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await webhooks[0].delete(reason=constants.messages.deleted_channel)
        channel_name = channel.name
        await ctx.send(f"Deleting channel {channel_name} from database...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/delete_channel.sql", "r")
                as sql_delete_channel,
        ):
            delete_channel = sql_delete_channel.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(delete_channel, (channel_id,))
        db.commit()
        db.close()
        await ctx.send(constants.messages.update_db)

    @db_group.command(
        name="delete-cog",
        brief="Removes a cog.",
        help="""
            Removes the given BaseCog subclass from the entire database.
            This will also remove the cog from the bot and delete all
            its command records in the Commands table.
            """
    )
    async def delete_cog(
            self,
            ctx: commands.Context,
            cog_name: str = commands.parameter(
                description="Name of the cog"
            )
    ) -> None:
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        cog = self.bot.get_cog(cog_name)
        if (cog is None):
            await ctx.send(constants.messages.invalid_cog)
            return

        await ctx.send(f"Deleting channel {channel_name} from database...")
        command_names: List[Tuple[str]]
        for command in cog.walk_commands():
            command_names.append((command.qualified_name,))

        self.bot.remove_cog(cog_name)
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/delete_command.sql", "r")
                as sql_delete_cog,
            open(f"{sql_dir}/delete_cog.sql", "r")
                as sql_delete_command,
        ):
            delete_cog = sql_delete_cog.read()
            delete_command = sql_delete_command.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.executemany(delete_command, command_names)
        cursor.execute(delete_cog, (cog_name,))
        db.commit()
        db.close()
        await ctx.send(constants.messages.db_update)

    @db_group.command(
        name="delete-user-command",
        brief="Removes a user entry tied to a command.",
        help="""
            Removes a given user from a specified command. If the user does
            not have access to anymore commands after removal, the user is
            completely removed from the database.
            """
    )
    async def delete_user_command(
            self,
            ctx: commands.Context,
            user_id: int = commands.parameter(
                description="ID of the user"
            ),
            *,
            command_name: str = commands.parameter(
                description="Name of the command"
            )
    ) -> None:
        user = await self.bot.fetch_user(user_id)
        username = user.name
        command = self.bot.get_command(command_name)
        await ctx.send(f"Deleting user {username} from "
                       f"command {command_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_user_commands_like.sql", "r")
                as sql_select_user_commands_like,
            open(f"{sql_dir}/delete_orphan_users.sql", "r")
                as sql_delete_orphan_users,
            open(f"{sql_dir}/delete_orphan_user_cogs.sql", "r")
                as sql_delete_orphan_user_cogs,
            open(f"{sql_dir}/delete_user_command.sql", "r")
                as sql_delete_user_command,
        ):
            select_commands_like = sql_select_user_commands_like.read()
            delete_user_command_records = sql_delete_user_command.read()
            delete_orphan_user_cogs = sql_delete_orphan_user_cogs.read()
            delete_orphan_users = sql_delete_orphan_users.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(delete_user_command_records, (user_id, command_name))
        for parent in command.parents:
            cursor.execute(select_commands_like,
                           (f"{parent.qualified_name}%",))
            command_name_records = cursor.fetchall()
            if (len(command_name_records) == 1):
                cursor.execute(
                    delete_user_command_records,
                    (user_id, parent.qualified_name)
                )
            else:
                break

        cursor.execute(delete_orphan_user_cogs)
        cursor.execute(delete_orphan_users)
        db.commit()
        db.close()
        await ctx.send(constants.messages.db_update)

    @db_group.command(
        name="delete-channel-command",
        brief="Removes a channel entry tied to a command.",
        help="""
            Removes a given channel from a specified command. If the channel
            does not have access to anymore commands after removal, the channel
            is completely removed from the database.
            """
    )
    async def delete_channel_command(
            self,
            ctx: commands.Context,
            channel_id: int = commands.parameter(
                description="ID of the channel"
            ),
            *,
            command_name: str = commands.parameter(
                description="Name of the command"
            )
    ) -> None:
        channel = await self.bot.fetch_channel(channel_id)
        channel_name = channel.name
        command = self.bot.get_command(command_name)
        await ctx.send(f"Deleting channel #{channel_name} "
                       f"from command {command_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_channel_commands_like.sql", "r")
                as sql_select_channel_commands_like,
            open(f"{sql_dir}/delete_channel_command.sql", "r")
                as sql_delete_channel_command,
            open(f"{sql_dir}/delete_orphan_channel_cogs.sql", "r")
                as sql_delete_orphan_channel_cogs,
            open(f"{sql_dir}/select_orphan_channels.sql", "r")
                as sql_select_orphan_channels,
            open(f"{sql_dir}/delete_orphan_channels.sql", "r")
                as sql_delete_orphan_channels,
        ):
            select_commands_like = sql_select_channel_commands_like.read()
            delete_channel_command_records = sql_delete_channel_command.read()
            delete_orphan_channel_cogs = sql_delete_orphan_channel_cogs.read()
            get_orphan_channels = sql_select_orphan_channels.read()
            delete_orphan_channels = sql_delete_orphan_channels.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(
            delete_channel_command_records,
            (channel_id, command_name)
        )
        for parent in command.parents:
            cursor.execute(select_commands_like, (f"{parent.qualified_name}%"))
            command_name_records = cursor.fetchall()
            if (len(command_name_records) == 1):
                cursor.execute(
                    delete_channel_command_records,
                    (channel_id, parent.qualified_name)
                )
            else:
                break

        cursor.execute(delete_orphan_channel_cogs)
        cursor.execute(get_orphan_channels)
        channel_records = cursor.fetchall()
        def pull_singleton(x): return x[0]
        channel_ids = list(map(pull_singleton, channel_records))
        cursor.execute(delete_orphan_channels)
        db.commit()
        db.close()
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        for channel_id in channel_ids:
            channel = await self.bot.fetch_channel(channel_id)
            webhooks = await channel.webhooks()
            await webhooks[0].delete(reason=constants.messages.deleted_channel)

        await ctx.send(constants.messages.db_update)

    @db_group.command(
        name="delete-user-cog",
        brief="Removes user access to all commands of a given cog.",
        help="""
            Removes all records linking the given user and all the commands of
            a given cog.
            """
    )
    async def delete_user_cog(
            self,
            ctx: commands.Context,
            user_id: int = commands.parameter(
                description="ID of the user"
            ),
            cog_name: str = commands.parameter(
                description="Name of the cog"
            )
    ) -> None:
        user = await self.bot.fetch_user(user_id)
        username = user.name
        cog = self.bot.get_cog(cog_name)
        await ctx.send(f"Deleting user {username} from cog {cog_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/delete_user_cog.sql", "r")
                as sql_delete_user_cog,
            open(f"{sql_dir}/delete_orphan_user_cogs.sql", "r")
                as sql_delete_orphan_user_cogs,
            open(f"{sql_dir}/delete_orphan_users.sql", "r")
                as sql_delete_orphan_users,
        ):
            delete_user_cog = sql_delete_user_cog.read()
            delete_orphan_user_cogs = sql_delete_orphan_user_cogs.read()
            delete_orphan_users = sql_delete_orphan_users.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(delete_user_cog, (user_id, cog_name))
        cursor.execute(delete_orphan_user_cogs)
        cursor.execute(delete_orphan_users)
        db.commit()
        db.close()
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await ctx.send(constants.messages.db_update)

    @db_group.command(
        name="delete-channel-cog",
        brief="Removes channel access to all commands of a given cog.",
        help="""
            Removes all records linking the given channel and all the commands of
            a given cog.
            """
    )
    async def delete_channel_cog(
            self,
            ctx: commands.Context,
            channel_id: int = commands.parameter(
                description="ID of the channel"
            ),
            cog_name: str = commands.parameter(
                description="Name of the cog"
            )
    ) -> None:
        channel = await self.bot.fetch_channel(channel_id)
        channel_name = channel.name
        cog = self.bot.get_cog(cog_name)
        await ctx.send(f"Deleting channel {channel_name} from cog {cog_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/delete_channel_cog.sql", "r")
                as sql_delete_channel_cog,
            open(f"{sql_dir}/delete_orphan_channel_cogs.sql", "r")
                as sql_delete_orphan_channel_cogs,
            open(f"{sql_dir}/select_orphan_channels.sql", "r")
                as sql_select_orphan_channels,
            open(f"{sql_dir}/delete_orphan_channels.sql", "r")
                as sql_delete_orphan_channels,
        ):
            delete_channel_cog = sql_delete_channel_cog.read()
            delete_orphan_channel_cogs = sql_delete_orphan_channel_cogs.read()
            get_orphan_channels = sql_select_orphan_channels.read()
            delete_orphan_channels = sql_delete_orphan_channels.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(delete_channel_cog, (channel_id, cog_name))
        cursor.execute(delete_orphan_channel_cogs)
        cursor.execute(get_orphan_channels)
        channel_records = cursor.fetchall()
        def pull_singleton(x): return x[0]
        channel_ids = list(map(pull_singleton, channel_records))
        cursor.execute(delete_orphan_channels)
        db.commit()
        db.close()
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        for channel_id in channel_ids:
            channel = await self.bot.fetch_channel(channel_id)
            webhooks = await channel.webhooks()
            await webhooks[0].delete(reason=constants.messages.deleted_channel)

        await ctx.send(constants.messages.db_update)

    @db_group.command(
        name="delete-command",
        brief="Removes a command.",
        help="""
            Removes the given command. This will simply remove the record from
            the database, it does not disable the command.
            """
    )
    async def delete_command(
            self,
            ctx: commands.Context,
            *,
            command_name: str = commands.parameter(
                description="Name of the command"
            )
    ) -> None:
        await ctx.send(f"Removing command {command_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/delete_command.sql", "r")
                as sql_delete_command,
            open(f"{sql_dir}/delete_orphan_users.sql", "r")
                as sql_delete_orphan_users,
            open(f"{sql_dir}/select_orphan_channels.sql", "r")
                as sql_select_orphan_channels,
            open(f"{sql_dir}/delete_orphan_channels.sql", "r")
                as sql_delete_orphan_channels,
        ):
            delete_command_record = sql_delete_command.read()
            delete_orphan_users = sql_delete_orphan_users.read()
            get_orphan_channels = sql_select_orphan_channels.read()
            delete_orphan_channels = sql_delete_orphan_channels.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        db.execute("PRAGMA FOREIGN_KEYS = ON")
        cursor = db.cursor()
        cursor.execute(delete_command_record, (command_name,))
        cursor.execute(delete_orphan_users)
        cursor.execute(get_orphan_channels)
        channel_records = cursor.fetchall()
        def pull_singleton(x): return x[0]
        channel_ids = list(map(pull_singleton, channel_records))
        cursor.execute(delete_orphan_channels)
        db.commit()
        db.close()
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        for channel_id in channel_ids:
            channel = await self.bot.fetch_channel(channel_id)
            webhooks = await channel.webhooks()
            await webhooks[0].delete(reason=constants.messages.deleted_channel)

        await ctx.send(constants.messages.db_update)

    async def cog_load(self) -> None:
        self.register_commands()
        await self.create_webhooks()
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        print(eval(constants.messages.loaded_cog))

    async def cog_unload(self) -> None:
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        print(eval(constants.messages.unloaded_cog))


async def setup(bot) -> None:
    await bot.add_cog(BaseCogDatabase(bot))
