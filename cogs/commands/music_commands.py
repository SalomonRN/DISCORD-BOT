import discord
from discord import app_commands
import discord.ext.commands
from discord.ext import commands
import asyncio
import discord
from discord.ext import commands, tasks
from discord.ext import commands
import discord.ext
import discord.ext.commands
import os
from dotenv import load_dotenv
import yt_dlp
import queue

load_dotenv()


class YouTubeCog(discord.ext.commands.Cog):
    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 200M",
        "options": "-vn",
    }
    GLOBAL_VOLUME = 0.10
    QUEU_SONG = queue.Queue()

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f"Hello {member.name}~")
        else:
            await ctx.send(f"Hello {member.name}... This feels familiar.")
        self._last_member = member

    @commands.command(name="leave", help="To make the bot leave the voice channel")
    async def leave(self, ctx: discord.ext.commands.Context):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()

    @commands.command(name="pause", help="This command pauses the song")
    async def pause(self, ctx: discord.ext.commands.Context):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name="resume", help="Resumes the song")
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send(
                "The bot was not playing anything before this. Use p command"
            )

    @commands.command(name="stop", help="Stops the song")
    async def stop(self, ctx: discord.ext.commands.Context):
        voice_client: discord.voice_client.VoiceClient = ctx.message.guild.voice_client

        if voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Cancion detenida")
        else:
            await ctx.send("No hay musica sonando!")

    @commands.command("v")
    async def volume(self, ctx: discord.ext.commands.Context, volume: int):

        try:
            volume = float(volume) / 100
            if volume == 0:
                raise ValueError()
            self.GLOBAL_VOLUME = volume
            self.VOLUME_CLIENT.volume = volume
        except ValueError:
            return await ctx.send("Valor no valido. El valor debe ser entre 1 a 100")
        except Exception as e:
            print(type(e))
            print(e)

    # https://stackoverflow.com/questions/75493436/why-is-the-ffmpeg-process-in-discordpy-terminating-without-playing-anything

    @commands.command("p")
    async def play(self, ctx: discord.ext.commands.Context, url: str = None):
        # REGEXP para saber si es una URL valida!
        pass

        if not ctx.author.voice:
            return await ctx.send("Debes estar en un voice")

        user_voice_channel = ctx.author.voice.channel

        if ctx.voice_client and ctx.voice_client.channel != user_voice_channel:
            return await ctx.send("Actualmente el bot está en otro voice :/")

        if ctx.voice_client is None:
            await user_voice_channel.connect()

        # Si está vacia reproducimos la cancion de una vez

        if ctx.voice_client.is_playing():
            await self.add_song(url)
            return await ctx.send("Cancion agregada!!")

        source = discord.FFmpegPCMAudio(await self.get_url(url), **self.FFMPEG_OPTIONS)
        volume_source = discord.PCMVolumeTransformer(source, volume=self.GLOBAL_VOLUME)
        self.VOLUME_CLIENT = volume_source

        # https://stackoverflow.com/questions/75493436/why-is-the-ffmpeg-process-in-discordpy-terminating-without-playing-anything

        ctx.voice_client.play(
            volume_source,
            after=lambda ex: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop),
        )
        return

    # De lo contrario colocamos la cancion en la cola

    @commands.command("q")
    async def queu_song(self, ctx: discord.ext.commands.Context):
        print(list(self.QUEU_SONG.queue))
        return await ctx.send(
            f"Hay un aproximado de '{self.QUEU_SONG.qsize()}' canciones en cola"
        )

    # ---------------
    async def add_song(self, url: str):
        try:
            self.QUEU_SONG.put_nowait(url)
        except queue.Full:
            raise Exception("La cola está llena actualmente")
            print("QUEU LLENA----------------------")

    async def get_url(self, url: str):

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
            "quiet": False,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        # https://stackoverflow.com/questions/75680967/using-yt-dlp-in-discord-py-to-play-a-song
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            secret = url if url else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            info = ydl.extract_info(secret, download=False)
            url2 = info["url"]
            return url2

    async def play_next(self, ctx):
        if not self.QUEU_SONG.empty():
            link = self.QUEU_SONG.get_nowait()
            await self.play(ctx, url=link)
