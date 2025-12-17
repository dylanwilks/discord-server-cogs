import os
import asyncio
import functools
import discord
import yt_dlp 
from discord.ext import commands
from typing import Final, Dict, Any, Self
from discord import FFmpegPCMAudio
from lib.orderedcog import OrderedCog
from lib.config import Config

YT_DLP_OPTS: Final[Dict[str, Any]] = {
        'format': 'worstaudio',
        'format-sort': 'tbr',
        'noplaylist': True,
        'default_search': 'auto',
        'source_address': '192.168.0.35'
}

FFMPEG_OPTS: Final[Dict[str, Any]] = {
        'options': '-vn'
}

ytdlp: Final = yt_dlp.YoutubeDL(YT_DLP_OPTS)


class YTDLPSource(discord.PCMVolumeTransformer):
    def __init__(
            self, 
            source: discord.AudioSource, 
            *, 
            data: dict, 
            volume: float=1.0,
    ) -> None:
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def create_source(
            cls,
            ctx: commands.Context,
            search: str,
            *,
            loop=None,
            download=False
    ) -> Self:
        loop = loop or asyncio.get_event_loop()
        to_run = functools.partial(
                ytdlp.extract_info, 
                url=search, 
                download=download
        )
        data = await loop.run_in_executor(None, to_run)

        if ('entries' in data):
            data = data['entries'][0]

        source = ytdlp.prepare_filename(data) if download else data['url']

        return cls(
            FFmpegPCMAudio(data['url'], **FFMPEG_OPTS), 
            data=data
        )


class Youtube(OrderedCog, description=f"Plays audio from Youtube."):
    class VoiceChannelError(commands.CommandError):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

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
        name="yt",
        brief=f"Group of commands for Youtube functionality.",
        help=f"""
            Group composing of commands that will control the audio the bot is
            playing through Youtube.
            """,
        invoke_without_command=True
    )
    async def yt_group(self, ctx: commands.Context):
        constants = Config.from_json(os.environ["BOT_CONSTANTS"])
        await ctx.send(eval(constants.messages.servers.no_subcommand))

    @yt_group.command(
        brief=f"Plays the given video.",
        help=f"""
            Takes as input the name of the video or its URL. If the name
            is given, the bot will play the first search result.
            """
    )
    @OrderedCog.assert_perms(user_perm=0, channel_perm=0)
    async def play(self, ctx: commands.Context, *, search: str):
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise self.VoiceChannelError(
                "Must be in a channel to use this command."
            )

        await self.connect(ctx, channel)
        async with ctx.typing():
            source = await YTDLPSource.create_source(ctx, search)
            ctx.voice_client.play(source)

        await ctx.send(f"Now playing: {source.title}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Youtube(bot))
