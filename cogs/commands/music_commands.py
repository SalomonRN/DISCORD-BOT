import discord
import discord.ext
import discord.ext.commands
from discord import app_commands
from discord.ext import commands, tasks
import discord.ext.commands
from dotenv import load_dotenv
from typing import Tuple
from random import choices
import asyncio
import yt_dlp
import queue
import os
import re
load_dotenv()


class YouTubeCog(discord.ext.commands.Cog):
    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 200M",
        "options": "-vn",
    }
    GLOBAL_VOLUME = 0.10
    SERVERS_DATA = {}
    MAX_LEN_QUEU = 10
    QUEU_SONG = queue.Queue()
    MESSAGES = [
        "🎧 Alistándome para ser el DJ de la noche...",
        "🕺 Subiendo el volumen, porque la fiesta empieza ya!",
        "🎶 Cargando vinilos virtuales... listo para pinchar música!",
        "🥁 Afinando los bajos para que tiemble el servidor...",
        "🎤 Micrófono en mano, que empiece el show!",
        "🎹 Poniendo los beats más frescos en la bandeja...",
        "🚀 Listo para despegar con un viaje musical intergaláctico!",
        "🍻 Sirviendo temazos como si fueran cervezas frías...",
        "🔥 Reproduciendo música tan buena que necesitarás extintor.",
        "🐱 El DJ gato ha llegado... prepárense para maullar con ritmo.",
        "🕶️ Sacando los temazos secretos de mi maleta de DJ...",
        "📀 Insertando el disco que hará que todos olviden estudiar.",
        "🤖 Modo robot activado: calculando el beat drop perfecto.",
        "💃 Cargando la playlist oficial de las fiestas épicas...",
        "⚡ La energía sube... ¡DJ BOT en la casa!"
    ]
    last_message = None

    def __init__(self, bot: discord.Client):
        self.bot = bot

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
    async def volume(self, ctx: discord.ext.commands.Context, volume: int = None ):
        if not volume:
            return await ctx.send(f"El volumen actual es de: {self.VOLUME_CLIENT.volume}")
            
        try:
            volume = float(volume) / 100
            if volume == 0:
                raise ValueError()
            self.GLOBAL_VOLUME = volume
            self.VOLUME_CLIENT.volume = volume
            return await ctx.send("Volumen cambiado ;)")
        except ValueError:
            return await ctx.send("Valor no valido. El valor debe ser entre 1 a 100")
        except Exception as e:
            print(type(e))
            print(e)

    # https://stackoverflow.com/questions/75493436/why-is-the-ffmpeg-process-in-discordpy-terminating-without-playing-anything
    @commands.command("p", aliases=["play", "music"])
    async def play(self, ctx: discord.ext.commands.Context, url: str = None):
        
        if not url:
            embed = discord.Embed(colour=0x043548)
            embed.title ="📢 Cómo usar el comando de Música"
            embed.description = (
                f"¡Hora de ponerle ritmo al servidor! 🎶\n"
                f"🎶 ¿Quieres escuchar música de YouTube fácilmente? Pues sí, no? Sino no hubeiras usado este comando 🙄 \n\n"
                f"💡 Recuerda que el prefijo por defecto es {self.bot.command_prefix}, aunque puede variar según el servidor.\n\n"
                f"🔸 Reproducir una canción desde YouTube:\n"
                f"**{self.bot.command_prefix}p <URL>**\n"
                f"  ➡️ El bot buscará la canción y la reproducirá en tu canal de voz.\n"
                f"  ⚠️ Debes estar conectado a un canal de voz.\n\n"
                f"🔸 Pausar la música actual:\n"
                f"**{self.bot.command_prefix}pause**\n"
                f"  ➡️ Pausa la reproducción actual.\n\n"
                f"🔸 Reanudar la música pausada:\n"
                f"**{self.bot.command_prefix}resume**\n"
                f"  ➡️ Continúa la canción donde la dejaste.\n\n"
                f"🔸 Saltar a la siguiente canción de la cola:\n"
                f"**{self.bot.command_prefix}skip**\n"
                f"  ➡️ Reproduce la siguiente canción.\n\n"
                f"🔸 Mostrar la cola de canciones:\n"
                f"**{self.bot.command_prefix}q**\n"
                f"  ➡️ Verás la lista completa de temas en espera.\n\n"
                f"🔸 Detener la música y limpiar la cola:\n"
                f"**{self.bot.command_prefix}stop**\n"
                f"  ➡️ El bot se detendrá y saldrá del canal de voz.\n\n"
                f"🔸 Este comando tiene los siguientes alias: *play* *music* 🎵"
            )
            return await ctx.send(embed=embed, ephemeral=True)
        
        if not ctx.author.voice:
            return await ctx.send("Debes estar en un voice")

        user_voice_channel = ctx.author.voice.channel

        if ctx.voice_client and ctx.voice_client.channel != user_voice_channel:
            return await ctx.send("Actualmente el bot está en otro voice :/")
        
        
        vali_url = self.validate_youtube_url(url)
        if not vali_url[0]:
            return await ctx.send(vali_url[1])

        if ctx.voice_client is None:
            await user_voice_channel.connect()

        # Si está vacia reproducimos la cancion de una vez

        if ctx.voice_client.is_playing():
            await self.add_song(url, ctx.guild.id)
            return await ctx.send("Cancion agregada!!")
        
        message = self.get_message_response()
        await ctx.send(message)
        source = discord.FFmpegPCMAudio(await self.get_url(url), **self.FFMPEG_OPTIONS)
        volume_source = discord.PCMVolumeTransformer(source, volume=self.GLOBAL_VOLUME)
        self.VOLUME_CLIENT = volume_source

        # https://stackoverflow.com/questions/75493436/why-is-the-ffmpeg-process-in-discordpy-terminating-without-playing-anything

        ctx.voice_client.play(
            volume_source,
            after=lambda ex: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop),
        )
        
    @commands.command("q")
    async def queu_song(self, ctx: discord.ext.commands.Context):
        print(list(self.QUEU_SONG.queue))
        return await ctx.send(
            f"Hay un aproximado de '{self.QUEU_SONG.qsize()}' canciones en cola"
        )

    # ---------------
    def get_message_response(self):
        
        message = choices(self.MESSAGES)[0]
        while message == self.last_message:
            message = choices(self.MESSAGES)
        self.last_message = message
        return message
    
    def validate_youtube_url(self, url: str) -> Tuple[bool, str]:
        if not url.startswith("https://"):
            return False, "Asegurate que la URL inicie con: *https://www.youtube.com/* o *https://youtu.be/*"
        
        if not url.startswith(("https://www.youtube.com", "https://youtu.be")):
            return False, "El dominio de la url no es valido, asegurate de que sea *https://www.youtube.com/* o *https://youtu.be/*"
        
        if "https://youtu.be/" in url:
            return True, url.split("?")[0]
        if "https://www.youtube.com" in url:
            print("------------------------------------")
            return True, url.split("&")[0]
        
        return False, "La verdad no pude valdiar el Link, porfavor usa el comando */error* y deja el reporte del bug junto con el link que usaste \n\n. *Nota* Colocar como codigo 987 para que se me sea mas facil rastrear el tipo de error 😉"
    
    async def add_song(self, url: str, server_id: int):
        try:
            if server_id not in self.SERVERS_DATA:
                self.SERVERS_DATA[server_id] = {}
            self.SERVERS_DATA[server_id]['queu'].put_nowait(url)
            # self.QUEU_SONG.put_nowait(url)
        except queue.Full:
            raise Exception("La cola está llena actualmente")

    async def get_url(self, url: str):

        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "ios"]
                }
            },
        }

        # https://stackoverflow.com/questions/75680967/using-yt-dlp-in-discord-py-to-play-a-song
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            secret = url if url else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            info = ydl.extract_info(secret, download=False)
            url2 = info["url"]
            match = re.search(r"expire=(\d+)", url2)

            return url2

    async def play_next(self, ctx):
        if not self.QUEU_SONG.empty():
            link = self.QUEU_SONG.get_nowait()
            await self.play(ctx, url=link)

