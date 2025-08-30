import discord
import discord.ext.commands
from discord import app_commands
from core.db.logs.mongo import create_log_bug

class LogCommands(discord.ext.commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @app_commands.command(name="error", description="Reporta un bug o error que haya ocurrido.")
    @app_commands.describe(description="Descripcion de como sucedió el error. Que comando usaste y que opciones colocaste.", code="Código del error que el bot arrojó.")
    async def error(self, interaction: discord.Interaction, description: str, code: str):
        await create_log_bug(description, interaction.guild.name, interaction.user.name, code, None)
        return await interaction.response.send_message("Gracias por reportar el bug, lo revisaré en cuanto pueda 😊", ephemeral=True)

    @app_commands.command(name="configure_bot", description="Configura el bot en el servidor. (Aún no implementado)")
    async def configure_bot(self, interaction: discord.Interaction):
        return await interaction.response.send_message("Aún no la he hecho, y no quiero quitarla :)", ephemeral=True)
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("No tienes permisos para ejecutar este comando.",
                                                           ephemeral=True, delete_after=4)
        
        # LO HARÉ CON MODALES
        
        return await interaction.response.send_message("Configurando el bot en el servidor...", ephemeral=True)

    @staticmethod
    async def send_log_error(server: discord.Guild, message: str):
        # Esto lo traeré de la base de datos, por ahora lo dejo así
        # channel = mongo.get_server(server.id).get("logs_channel")
        channel = 0 
        if not channel:
            await server.owner.create_dm()
            return await server.owner.send("Ey, parece que no tienes el canal de logs configurado, porfa configura el canal de logs con el comando /configure_bot")
        await server.get_channel(channel).send(message)
