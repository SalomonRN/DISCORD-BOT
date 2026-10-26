import os
import asyncio
import discord
import discord.ext
import discord.ext.commands
from discord import app_commands
from discord.ext import voice_recv
from utils.utils import create_audio, load_libopus

SOUND_FILE = "molestar.mp3"
SOUND_TEXT = "¡Cállate ya!"
# Segundos mínimos entre un audio y el siguiente, para que no sea un spam infinito
COOLDOWN = 3.0


class AnnoySink(voice_recv.AudioSink):
    """Sink que solo detecta cuándo habla el usuario objetivo, sin decodificar el audio."""

    def __init__(self, target_id: int, on_target_speaking):
        super().__init__()
        self.target_id = target_id
        self.on_target_speaking = on_target_speaking

    def wants_opus(self) -> bool:
        # Con DAVE (E2EE) el audio llega cifrado y decodificarlo falla. No necesitamos
        # el contenido: basta con saber que llegan paquetes del usuario.
        return True

    def write(self, user, data):
        pass

    def cleanup(self):
        pass

    # Corre en un hilo del lector de voz, no en el event loop
    @voice_recv.AudioSink.listener()
    def on_voice_member_speaking_start(self, member: discord.Member):
        if member.id == self.target_id:
            self.on_target_speaking()


class AnnoyCog(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot: discord.ext.commands.Bot = bot
        # guild_id -> id del usuario al que se está molestando
        self.targets: dict[int, int] = {}
        self.last_played: dict[int, float] = {}

    @app_commands.command(name="molestar", description="El bot entra a tu voice y suena un audio cada vez que esa persona hable 😈")
    @app_commands.describe(usuario="La persona a la que quieres molestar.")
    async def molestar(self, interaction: discord.Interaction, usuario: discord.Member):
        await interaction.response.defer(ephemeral=True)

        if usuario.bot:
            return await interaction.followup.send("No puedo molestar a un bot 🤖", ephemeral=True)
        if not usuario.voice or not usuario.voice.channel:
            return await interaction.followup.send(f"**{usuario.display_name}** no está en un canal de voz.", ephemeral=True)
        if not load_libopus():
            return await interaction.followup.send("⚠️ Error al cargar la librería Opus. Código: 4", ephemeral=True)

        if not os.path.exists(SOUND_FILE):
            await asyncio.to_thread(create_audio, SOUND_TEXT, SOUND_FILE)

        channel = usuario.voice.channel
        bot_vc = interaction.guild.voice_client

        try:
            # Para escuchar se necesita un VoiceRecvClient; si el bot está conectado con
            # el cliente normal (por ejemplo tras un /message), hay que reconectar.
            if bot_vc and not isinstance(bot_vc, voice_recv.VoiceRecvClient):
                await bot_vc.disconnect(force=True)
                bot_vc = None

            if not bot_vc:
                bot_vc = await channel.connect(cls=voice_recv.VoiceRecvClient, timeout=30.0)
            elif bot_vc.channel != channel:
                await bot_vc.move_to(channel, timeout=30.0)

            if bot_vc.is_listening():
                bot_vc.stop_listening()

            guild_id = interaction.guild.id
            loop = self.bot.loop
            sink = AnnoySink(usuario.id, lambda: loop.call_soon_threadsafe(self._play_sound, guild_id))
            bot_vc.listen(sink)
            self.targets[guild_id] = usuario.id
        except Exception as error:
            print(f"❌ Error en /molestar: {error}")
            return await interaction.followup.send("⚠️ No pude conectarme al canal de voz.", ephemeral=True)

        await interaction.followup.send(f"😈 Molestando a **{usuario.display_name}** en **{channel.name}**. Usa `/dejar_de_molestar` para parar.", ephemeral=True)

    @app_commands.command(name="dejar_de_molestar", description="El bot deja de molestar y sale del canal de voz.")
    async def dejar_de_molestar(self, interaction: discord.Interaction):
        if interaction.guild.id not in self.targets:
            return await interaction.response.send_message("No estoy molestando a nadie 😇", ephemeral=True)

        await self._stop(interaction.guild)
        await interaction.response.send_message("😇 Ya dejé de molestar.", ephemeral=True)

    @discord.ext.commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if self.targets.get(member.guild.id) != member.id:
            return

        bot_vc = member.guild.voice_client
        if not after.channel:
            # Se salió del voice: dejamos de molestar
            await self._stop(member.guild)
        elif bot_vc and bot_vc.channel != after.channel:
            # Se cambió de canal: lo seguimos
            await bot_vc.move_to(after.channel)

    def _play_sound(self, guild_id: int):
        guild = self.bot.get_guild(guild_id)
        bot_vc = guild.voice_client if guild else None
        if not bot_vc or not bot_vc.is_connected() or bot_vc.is_playing():
            return

        now = self.bot.loop.time()
        if now - self.last_played.get(guild_id, 0) < COOLDOWN:
            return

        self.last_played[guild_id] = now
        bot_vc.play(discord.FFmpegPCMAudio(SOUND_FILE))

    async def _stop(self, guild: discord.Guild):
        self.targets.pop(guild.id, None)
        self.last_played.pop(guild.id, None)

        bot_vc = guild.voice_client
        if bot_vc:
            if isinstance(bot_vc, voice_recv.VoiceRecvClient) and bot_vc.is_listening():
                bot_vc.stop_listening()
            await bot_vc.disconnect()
