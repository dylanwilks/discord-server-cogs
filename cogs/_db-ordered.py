import os
import sqlite3
import discord
from discord.ext import commands
from lib.basecog import BaseCog
from lib.orderedcog import OrderedCog
from lib.config import Config


class OrderedCogDatabase(
        BaseCog,
        name="db-ordered",
        description="Commands for the database relating to OrderedCog."
):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.db_cog = self.bot.get_cog("db-base")

    @commands.command(
        name="print-user-perms-table",
        brief="Prints all records of the UserPerms table.",
        help="""
            Displays records within the UserPerms table as tuples.
            Automatically converts user IDs into usernames.
            """
    )
    async def print_user_perms_table(
            self,
            ctx: commands.Context
    ) -> None:
        await ctx.send(f"Fetching UserPerms table...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_user_perms_table.sql", "r")
                as sql_select_user_perms_table,
        ):
            get_user_perms_records = sql_select_user_perms_table.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        try:
            db.execute("PRAGMA FOREIGN_KEYS = ON")
            cursor = db.cursor()
            cursor.execute(get_user_perms_records)
            user_perms_records = cursor.fetchall()
        finally:
            db.close()

        message = ""
        message_limit = config.settings.message_limit
        for record in user_perms_records:
            m_record = list(record)
            user = await self.bot.fetch_user(record[0])
            m_record[0] = user.name
            new_row = str(tuple(m_record)) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @commands.command(
        name="print-channel-perms-table",
        brief="Prints all records of the ChannelPerms table.",
        help="""
            Displays records within the ChannelPerms table as tuples.
            Automatically converts channel IDs into channel names.
            """
    )
    async def print_channel_perms_table(
            self,
            ctx: commands.Context
    ) -> None:
        await ctx.send(f"Fetching ChannelPerms table...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_channel_perms_table.sql", "r")
                as sql_select_channel_perms_table,
        ):
            get_channel_perms_records = sql_select_channel_perms_table.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        try:
            db.execute("PRAGMA FOREIGN_KEYS = ON")
            cursor = db.cursor()
            cursor.execute(get_channel_perms_records)
            channel_perms_records = cursor.fetchall()
        finally:
            db.close()

        message = ""
        message_limit = config.settings.message_limit
        for record in channel_perms_records:
            m_record = list(record)
            channel = await self.bot.fetch_channel(record[0])
            m_record[0] = '#' + channel.name
            new_row = str(tuple(m_record)) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @commands.command(
        name="print-cog-user-perms",
        brief="Prints records in UserPerms matching the given cog.",
        help="""
            Displays records from the UserPerms table with the given cog name as
            foreign key. Cog provided must be a subclass of OrderedCog.
            Automatically converts the user ID into the corresponding username.
            """
    )
    async def print_cog_user_perms(
            self,
            ctx: commands.Context,
            cog_name: str = commands.parameter(
                description="Name of the cog"
            )
    ) -> None:
        cog = self.bot.get_cog(cog_name)
        if (cog is None or
                not issubclass(type(cog), OrderedCog)):
            await ctx.send("Invalid cog name.")
            return

        await ctx.send(f"Fetching UserPerms records linked to {cog_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_cog_user_perm_records.sql", "r")
                as sql_select_cog_user_perm_records,
        ):
            get_cog_users = sql_select_cog_user_perm_records.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        try:
            db.execute("PRAGMA FOREIGN_KEYS = ON")
            cursor = db.cursor()
            cursor.execute(get_cog_users, (cog_name,))
            cog_user_records = cursor.fetchall()
        finally:
            db.close()

        message = ""
        message_limit = config.settings.message_limit
        for record in cog_user_records:
            m_record = list(record)
            user = await self.bot.fetch_user(record[0])
            m_record[0] = user.name
            new_row = str(tuple(m_record)) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @commands.command(
        name="print-cog-channel-perms",
        brief="Prints records in ChannelPerms matching the given cog.",
        help="""
            Displays records from the ChannelPerms table with the given cog name
            as foreign key. Cog provided must be a subclass of OrderedCog.
            Automatically converts the channel ID into the corresponding channel
            name.
            """
    )
    async def print_cog_channel_perms(
            self,
            ctx: commands.Context,
            cog_name: str = commands.parameter(
                description="Name of the cog"
            )
    ) -> None:
        cog = self.bot.get_cog(cog_name)
        if (cog is None or
                not issubclass(type(cog), OrderedCog)):
            await ctx.send("Invalid cog name.")
            return

        await ctx.send(f"Fetching ChannelPerms records linked to {cog_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/select_cog_channel_perm_records.sql", "r")
                as sql_select_cog_channel_perm_records,
        ):
            get_cog_channels = sql_select_cog_channel_perm_records.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        try:
            db.execute("PRAGMA FOREIGN_KEYS = ON")
            cursor = db.cursor()
            cursor.execute(get_cog_channels, (cog_name,))
            cog_channel_records = cursor.fetchall()
        finally:
            db.close()

        message = ""
        message_limit = config.settings.message_limit
        for record in cog_channel_records:
            m_record = list(record)
            channel = await self.bot.fetch_channel(record[0])
            m_record[0] = '#' + channel.name
            new_row = str(tuple(m_record)) + '\n'
            if (len(message) + len(new_row) > message_limit):
                await ctx.send(message)
                message = ""

            message += new_row

        await ctx.send(message)

    @commands.command(
        name="set-user-perm",
        brief="Sets the permission of a user for a specified cog.",
        help="""
            Sets the permission of a user for a specified cog that is a subclass of
            OrderedCog. If the user does not exist in the database, records will be
            generated, otherwise existing ones will be updated. This does not
            create records between the user and the commands of the cog, which will
            have to be done using other commands.
            """
    )
    async def set_user_perm(
            self,
            ctx: commands.Context,
            user_id: int = commands.parameter(
                description="ID of the user"
            ),
            cog_name: str = commands.parameter(
                description="Name of the cog"
            ),
            permission: int = commands.parameter(
                description="Permission level of the user",
                default=0
            )
    ) -> None:
        cog = self.bot.get_cog(cog_name)
        if (cog is None or
                not issubclass(type(cog), OrderedCog)):
            await ctx.send("Invalid cog name.")
            return

        try:
            user = await self.bot.fetch_user(user_id)
        except NotFound as e:
            await ctx.send("Invalid User ID.")
            return

        await ctx.send(f"Setting permission {permission} "
                       f"for user {user.name} "
                       f"in cog {cog_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/insert_user.sql", "r")
                as sql_insert_user,
            open(f"{sql_dir}/insert_user_perm.sql", "r")
                as sql_insert_user_perm,
        ):
            add_user = sql_insert_user.read()
            set_user_permission = sql_insert_user_perm.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        try:
            db.execute("PRAGMA FOREIGN_KEYS = ON")
            cursor = db.cursor()
            cursor.execute(add_user, (user_id,))
            constants = Config.from_json(os.environ["BOT_CONSTANTS"])
            if (cursor.rowcount):
                user_dm = await user.create_dm()
                await user_dm.send(eval(constants.messages.startup))

            cursor.execute(set_user_permission, (user_id, cog_name, permission))
            db.commit()
        finally:
            db.close()

        await ctx.send(constants.messages.db_update)

    @commands.command(
        name="set-channel-perm",
        brief="Sets the permission of a channel for a specified cog.",
        help="""
            Sets the permission of a channel for a specified cog that is a subclass
            of OrderedCog. If the channel does not exist in the database, records
            will be generated, otherwise existing ones will be updated. This does
            not create records between the channel and the commands of the cog,
            which will have to be done using other commands.
            """
    )
    async def set_channel_perm(
            self,
            ctx: commands.Context,
            channel_id: int = commands.parameter(
                description="ID of the channel"
            ),
            cog_name: str = commands.parameter(
                description="Name of the cog"
            ),
            permission: int = commands.parameter(
                description="Permission level of the channel",
                default=0
            )
    ) -> None:
        cog = self.bot.get_cog(cog_name)
        if (cog is None or
                not issubclass(type(cog), OrderedCog)):
            await ctx.send("Invalid cog name.")
            return

        try:
            channel = await self.bot.fetch_channel(channel_id)
        except NotFound as e:
            await ctx.send("Invalid Channel ID.")
            return

        await ctx.send(f"Setting permission {permission} "
                       f"for channel #{channel.name} "
                       f"in cog {cog_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/insert_channel.sql", "r")
                as sql_insert_channel,
            open(f"{sql_dir}/insert_channel_perm.sql", "r")
                as sql_insert_channel_perm,
        ):
            add_channel = sql_insert_channel.read()
            set_channel_permission = sql_insert_channel_perm.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        try:
            db.execute("PRAGMA FOREIGN_KEYS = ON")
            cursor = db.cursor()
            cursor.execute(add_channel, (channel_id,))
            constants = Config.from_json(os.environ["BOT_CONSTANTS"])
            if (cursor.rowcount):
                self.cog.create_webhook(channel)
                await channel.send(eval(constants.messages.startup))

            cursor.execute(set_channel_permission,
                           (channel_id, cog_name, permission))
            db.commit()
        finally:
            db.close()

        await ctx.send(constants.messages.db_update)

    @commands.command(
        name="remove-user-perm",
        brief="Removes the users permission level.",
        help="""
            Removes the record of the matching user and cog in the UserPerms table.
            Cog must be a subclass of OrderedCog.
            """
    )
    async def remove_user_cog_perm(
            self,
            ctx: commands.Context,
            cog_name: str = commands.parameter(
                description="Name of the cog"
            ),
            user_id: int = commands.parameter(
                description="ID of the user"
            )
    ) -> None:
        user = await self.bot.fetch_user(user_id)
        username = user.name
        await ctx.send(f"Removing record of user {username} and cog {cog_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/delete_user_cog_perm.sql", "r")
                as sql_delete_user_cog_perm,
        ):
            delete_user_cog_perm = sql_delete_user_cog_perm.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        try:
            db.execute("PRAGMA FOREIGN_KEYS = ON")
            cursor = db.cursor()
            cursor.execute(delete_user_cog_perm, (user_id, cog_name))
            db.commit()
        finally:
            db.close()

        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await ctx.send(constants.messages.db_update)

    @commands.command(
        name="remove-channel-perm",
        brief="Removes the channels permission level.",
        help="""
            Removes the record of the matching channel and cog in the ChannelPerms
            table. Cog must be a subclass of OrderedCog.
            """
    )
    async def remove_channel_cog_perm(
            self,
            ctx: commands.Context,
            cog_name: str = commands.parameter(
                description="Name of the cog"
            ),
            channel_id: int = commands.parameter(
                description="ID of the channel"
            )
    ) -> None:
        channel = await self.bot.fetch_channel(channel_id)
        channelname = channel.name
        await ctx.send(f"Removing record of channel {channelname} and cog "
                       f"{cog_name}...")
        config = Config.from_json(os.environ["BOT_CONFIG"])
        sql_dir = config.dir.sql
        db_path = os.environ["BOT_DB"]
        with (
            open(f"{sql_dir}/delete_channel_cog_perm.sql", "r")
                as sql_delete_channel_cog_perm,
        ):
            delete_channel_cog_perm = sql_delete_channel_cog_perm.read()

        db = sqlite3.connect(db_path, check_same_thread=False)
        try:
            db.execute("PRAGMA FOREIGN_KEYS = ON")
            cursor = db.cursor()
            cursor.execute(delete_channel_cog_perm, (channel_id, cog_name))
            db.commit()
        finally:
            db.close()

        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await ctx.send(constants.messages.db_update)

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
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        print(eval(constants.messages.loaded_cog))

    def cog_unload(self) -> None:
        for command in self.walk_commands():
            self.db_cog.db_group.remove_command(command.name)

        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        print(eval(constants.messages.unloaded_cog))


async def setup(bot) -> None:
    await bot.add_cog(OrderedCogDatabase(bot))
