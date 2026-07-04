import os
import asyncio
import functools
import discord
import yt_dlp
import subprocess
import asyncio
from collections import deque
from discord.ext import commands
from typing import Final, Dict, Any, Self, Deque
from discord import FFmpegPCMAudio
from lib.orderedcog import OrderedCog
from lib.config import Config


class YTDLPSource(discord.PCMVolumeTransformer):
    YT_DLP_OPTS: Final[Dict[str, Any]] = {
        'format': 'worstaudio',
        'extractaudio': True,
        'outtmpl': '%(title)s.%(ext)s',
        'format-sort': 'tbr',
        'noplaylist': True,
        'nocheckcertificate': True,
        'default_search': 'auto',
        'js_runtimes': {'quickjs': {'path': None}},
    }

    FFMPEG_OPTS: Final[Dict[str, Any]] = {
        'before_options': ('-reconnect 1 -reconnect_streamed 1 '
                           '-reconnect_delay_max 5'),
        'options': '-vn',
    }

    ytdlp: Final = yt_dlp.YoutubeDL(YT_DLP_OPTS)

    class YTDLPError(commands.CommandError):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    def __init__(
            self,
            source: discord.AudioSource,
            *,
            data: dict,
            volume: float = 0.5,
    ) -> None:
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @staticmethod
    async def _fetch_data(
            search: str,
            *,
            loop=None,
            download=False
    ) -> Union[str, io.BufferedIOBase]:
        loop = loop or asyncio.get_event_loop()
        to_run = functools.partial(
            YTDLPSource.ytdlp.extract_info,
            url=search,
            download=download
        )
        data = await loop.run_in_executor(None, to_run)

        if ('entries' in data):
            data = data['entries'][0]

        return data

    @classmethod
    async def _stream_from_data(cls, data: Union[str, io.BufferedIOBase]):
        source = discord.FFmpegPCMAudio(data['url'], **cls.FFMPEG_OPTS)
        source.read()

        return cls(source, data=data)

    @classmethod
    async def download_source(
            cls,
            search: str,
            *,
            loop=None,
    ) -> Self:
        data = cls._fetch_data(search, loop=loop, download=True)
        source = cls.ytdlp.prepare_filename(data)
        convert_to_raw_PCM = await asyncio.create_subprocess_exec(
            'ffmpeg',
            '-i', source,
            '-f', 's16le',
            '-ac', '2',
            '-acodec', 'pcm_s16le',
            'output.raw'
        )
        await convert_to_raw_PCM.wait()

        with open('output.raw') as audio:
            return cls(
                discord.PCMAudio(audio),
                data=data
            )


class Audio(OrderedCog, description=f"Plays audio."):
    class GuildSettings:
        def __init__(self, bot: commands.Bot):

            async def __empty():
                pass

            self.loop: bool = False
            self.rotate: bool = False
            self.voice_client_timeout: asyncio.Task = bot.loop.create_task(
                __empty())
            self.data_queue: Deque[Union[str, io.BufferedIOBase]] = deque()
            self.lock: asyncio.Lock = asyncio.Lock()

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)
        self.guild_settings: Dict[int, self.GuildSettings] = dict()

    async def timeout_callback(
            self,
            voice_client: discord.VoiceClient,
            timeout: int
    ) -> None:
        await asyncio.sleep(timeout)
        if (voice_client is not None):
            await voice_client.disconnect()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if (member.id == self.bot.user.id):
            settings = self.guild_settings[member.guild.id]
            if (after.channel is not None):
                settings.voice_client_timeout.cancel()
            else:
                settings.loop = False
                settings.rotate = False
                settings.data_queue.clear()
        else:

            def voice_to_id(x):
                return x.channel.id

            voice_clients = self.bot.voice_clients
            bot_voice_ids = list(map(voice_to_id, voice_clients))
            target_channel = (before.channel if after.channel is None
                              else after.channel)
            if (target_channel.id in bot_voice_ids):
                settings = self.guild_settings[member.guild.id]
                if (len(target_channel.members) == 1):
                    voice_client = voice_clients[bot_voice_ids.index(
                        target_channel.id)]
                    cog_config = Config.from_json(os.environ["BOT_COGS"]).audio
                    settings.voice_client_timeout = self.bot.loop.create_task(
                        self.timeout_callback(
                            voice_client,
                            cog_config.timeout_empty
                        )
                    )
                else:
                    settings.voice_client_timeout.cancel()

    class VoiceChannelError(commands.CommandError):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    class AudioError(commands.CommandError):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    def audio_playing_or_paused() -> Callable[[commands.Context], bool]:
        async def predicate(ctx: commands.Context) -> bool:
            if (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
                return True
            else:
                raise Audio.AudioError("No audio playing.")

        return commands.check(predicate)

    async def cog_check(self, ctx: commands.Context) -> bool:
        try:
            _channel = ctx.author.voice.channel
        except AttributeError:
            raise self.VoiceChannelError(
                "Must be in a channel to use this command."
            )

        return (await super().cog_check(ctx))

    async def cog_command_error(
            self,
            ctx: commands.Context,
            error: commands.CommandError
    ) -> None:
        match error:
            case(self.AudioError() |
                    self.VoiceChannelError() |
                    YTDLPSource.YTDLPError()):
                await ctx.send(error.message)
            case _:
                await super().cog_command_error(ctx, error)

    async def connect(
            self,
            ctx: commands.Context,
            channel: discord.VoiceChannel
    ) -> None:
        if (ctx.voice_client is not None):
            try:
                await ctx.voice_client.move_to(channel)
                return
            except asyncio.TimeoutError:
                raise self.VoiceChannelError(f"move_to({channel}) timed out.")

        await channel.connect()

    @commands.group(
        name="audio",
        brief=f"Group of commands for audio control.",
        help=f"""
            Group composing of commands that will control the audio the bot is
            playing.
            """,
        invoke_without_command=True
    )
    async def audio_group(self, ctx: commands.Context):
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await ctx.send(eval(constants.messages.servers.no_subcommand))

    @audio_group.group(
        name="yt",
        brief=f"Audio subgroup for Youtube commands.",
        help=f"""
            Subgroup of the audio group composing of commands for audio
            relating specifically to Youtube.
            """,
        invoke_without_command=True
    )
    @OrderedCog.assert_perms(user_perm=0, channel_perm=0)
    async def yt_group(self, ctx: commands.Context):
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await ctx.send(eval(constants.messages.servers.no_subcommand))

    @yt_group.command(
        name="play",
        brief=f"Plays the given audio.",
        help=f"""
            Takes as input the name of the audio or its URL. If a name
            is given, the bot will play the first search result.
            """
    )
    @OrderedCog.assert_perms(user_perm=0, channel_perm=0)
    async def yt_play(self, ctx: commands.Context, *, search: str) -> None:
        channel = ctx.author.voice.channel
        settings = self.guild_settings[ctx.guild.id]
        cog_config = Config.from_json(os.environ["BOT_COGS"]).audio

        async def after_callback() -> None:
            if (not settings.loop):
                if (settings.rotate):
                    settings.data_queue.rotate(-1)
                elif (settings.data_queue):
                    settings.data_queue.popleft()

            if (settings.data_queue):
                settings.voice_client_timeout.cancel()
                stream = await YTDLPSource._stream_from_data(
                    settings.data_queue[0]
                )
                ctx.voice_client.play(
                    stream,
                    after=(lambda e:
                           self.bot.loop.create_task(after_callback()))
                )

                if (not settings.loop):
                    await ctx.send(f"Now playing: "
                                   f"{settings.data_queue[0].get('title')}")
            else:
                async with settings.lock:
                    if (not settings.data_queue):
                        settings.voice_client_timeout = (
                            self.bot.loop.create_task(
                                self.timeout_callback(
                                    ctx.voice_client,
                                    cog_config.timeout_inactive
                                )
                            )
                        )

        async with ctx.typing():
            if (len(settings.data_queue) >= cog_config.queue_limit):
                raise self.AudioError(
                    "Queue limit %i reached." % cog_config.queue_limit
                )

            async with settings.lock:
                settings.voice_client_timeout.cancel()
                await self.connect(ctx, channel)
                data = await YTDLPSource._fetch_data(search)
                if (data is None):
                    raise YTDLPSource.YTDLPError("No matches found.")

                settings.data_queue.append(data)

            if (not (ctx.voice_client.is_playing() or
                     ctx.voice_client.is_paused())):
                stream = await YTDLPSource._stream_from_data(
                    settings.data_queue[0]
                )
                ctx.voice_client.play(
                    stream,
                    after=lambda t: self.bot.loop.create_task(after_callback())
                )

                await ctx.send(f"Now playing: {data.get('title')}")
            else:
                await ctx.send(f"Queued: {data.get('title')}")

    @yt_play.error
    async def catch_play_interrupt(self, ctx: commands.Context, error) -> None:
        settings = self.guild_settings[ctx.guild.id]
        if (not settings.data_queue):
            cog_config = Config.from_json(os.environ["BOT_COGS"]).audio
            settings.voice_client_timeout = self.bot.loop.create_task(
                self.timeout_callback(
                    ctx.voice_client,
                    cog_config.timeout_inactive
                )
            )

        if (isinstance(error, commands.CommandInvokeError)):
            if isinstance(error.original, AttributeError):
                await ctx.send("Connection interrupted.")

    @audio_group.command(
        name="queue",
        brief=f"Lists videos in the queue.",
        help=f"""
            Prints a list of videos in the queue.
            """
    )
    @OrderedCog.assert_perms(user_perm=0, channel_perm=0)
    async def audio_queue(self, ctx: commands.Context) -> None:
        settings = self.guild_settings[ctx.guild.id]
        audio_queue = ""
        for i, data in enumerate(settings.data_queue):
            audio_queue += "%i. %s" % (i, data.get('title'))
            if (i < len(settings.data_queue)):
                audio_queue += "\n"

        if (audio_queue):
            await ctx.send(audio_queue)
        else:
            await ctx.send("Nothing queued.")

    @audio_group.command(
        name="pause",
        brief=f"Pauses the audio.",
        help=f"""
            Pauses the audio playing. Disconnects if
            paused for a long period of time (default 30 mins).
            """
    )
    @OrderedCog.assert_perms(user_perm=0, channel_perm=0)
    @audio_playing_or_paused()
    async def audio_pause(self, ctx: commands.Context) -> None:
        settings = self.guild_settings[ctx.guild.id]
        if (ctx.voice_client.is_paused()):
            await ctx.send("Audio is already paused.")
        else:
            ctx.voice_client.pause()
            await ctx.send("Paused the audio.")
            cog_config = Config.from_json(os.environ["BOT_COGS"]).audio
            settings.voice_client_timeout = self.bot.loop.create_task(
                self.timeout_callback(
                    ctx.voice_client,
                    cog_config.timeout_paused
                )
            )

    @audio_group.command(
        name="resume",
        brief=f"Resumes the audio.",
        help=f"""
            Resumes the audio that was paused.
            """
    )
    @OrderedCog.assert_perms(user_perm=0, channel_perm=0)
    @audio_playing_or_paused()
    async def audio_resume(self, ctx: commands.Context) -> None:
        settings = self.guild_settings[ctx.guild.id]
        if (ctx.voice_client.is_paused()):
            settings.voice_client_timeout.cancel()
            ctx.voice_client.resume()
            await ctx.send("Resumed the audio.")
        else:
            await ctx.send("Audio is already playing.")

    @audio_group.command(
        name="stop",
        brief=f"Stops the current (or queued) audio.",
        help=f"""
            Stops the bot from playing the next specified queued songs
            (default: 1)
            """
    )
    @OrderedCog.assert_perms(user_perm=0, channel_perm=0)
    @audio_playing_or_paused()
    async def audio_stop(self, ctx: commands.Context, skip: int = 1) -> None:
        settings = self.guild_settings[ctx.guild.id]
        old_loop = settings.loop
        settings.loop = False

        if (settings.rotate):
            settings.data_queue.rotate(-skip + 1)
        else:
            tskip = len(
                settings.data_queue) if skip > len(
                settings.data_queue) else skip - 1
            for i in range(tskip):
                settings.data_queue.popleft()

        ctx.voice_client.stop()
        await ctx.send("Stopped the next %i audio(s)." % (skip))
        settings.loop = old_loop

    @audio_group.command(
        name="loop",
        brief=f"Loops the audio.",
        help=f"""
            Toggles audio loop.
            """
    )
    @OrderedCog.assert_perms(user_perm=0, channel_perm=0)
    async def audio_loop(self, ctx: commands.Context) -> None:
        settings = self.guild_settings[ctx.guild.id]
        settings.loop = not settings.loop
        await ctx.send(
            "Set loop -> " + ("true" if settings.loop else "false")
        )

    @audio_group.command(
        name="rotate",
        brief=f"Rotates the queue.",
        help=f"""
            Toggles queue rotation (effectively loops the whole playlist).
            """
    )
    @OrderedCog.assert_perms(user_perm=0, channel_perm=0)
    async def audio_rotate(self, ctx: commands.Context) -> None:
        settings = self.guild_settings[ctx.guild.id]
        settings.rotate = not settings.rotate
        await ctx.send(
            "Set rotate -> " + ("true" if settings.rotate else "false")
        )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        for guild in self.bot.guilds:
            self.guild_settings[guild.id] = self.GuildSettings(self.bot)

    async def cog_load(self) -> None:
        for guild in self.bot.guilds:
            self.guild_settings[guild.id] = self.GuildSettings(self.bot)

        await super().cog_load()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Audio(bot))
