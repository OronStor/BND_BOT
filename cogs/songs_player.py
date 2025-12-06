import asyncio
import re

import discord
from discord.ext import commands
from pathlib import Path
from yandex_music import Client

from config import settings
from utils.yandex_radio import Radio


class SongsPlayer(commands.Cog):
    """Cog для воспроизведения Моей Волны"""

    def __init__(self, bot):
        self.bot = bot
        self.radio_client = Radio(Client(token=settings.YANDEX_MUSIC_TOKEN))
        self.track = None

    @commands.command(name="play")
    async def play(self, ctx):
        """Воспроизвести MP3 файл"""
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("❌ Вы должны быть в голосовом канале!")

        voice_client = ctx.voice_client

        file_path = Path(self.__get_yandex_file_name())
        if not file_path.exists():
            await ctx.send(f"❌ Файл audio не найден!")

        if voice_client.is_playing():
            voice_client.stop()

        audio_source = discord.FFmpegOpusAudio(str(file_path))
        voice_client.play(audio_source)

        await ctx.send(f"🎵 Воспроизведение: **{file_path.name}**")


    @commands.command(name="pause")
    async def pause(self, ctx):
        """Поставить на паузу"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Пауза")
        else:
            await ctx.send("❌ Ничего не воспроизводится!")

    @commands.command(name="resume")
    async def resume(self, ctx):
        """Продолжить воспроизведение"""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Продолжаю")
        else:
            await ctx.send("❌ Воспроизведение не на паузе!")

    def __get_yandex_file_name(self):
        if not self.track:
            self.track = self.radio_client.start_radio("user:onyourwave", "")

        filename = self.__escape_filename(
            "{0} - {1}.mp3".format(", ".join(self.track.artists_name()), self.track.title)
        )
        print("[Radio] Download track:", filename)
        try:
            self.track.download(filename=f"data/audio/{filename}")
        except Exception as err:
            print("[Radio] Download failed:", err)
        return filename

    def  __escape_filename(self, name):
        return re.sub(r'[<>:"/\\|?*]', '', name)


async def setup(bot):
    await bot.add_cog(SongsPlayer(bot))