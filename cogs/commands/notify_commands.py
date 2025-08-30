import discord
import discord.ui as ui
import discord.ext
import discord.ext.commands
from discord import Colour, Embed, app_commands
from cogs.views import UserNotifyView
from core.db.users.errors import UserNotFound
from core.db.users.errors import UserNotFound
from core.db.users.mongo import update_user_notify_list, get_user

class NotifyCommands(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot: discord.ext.commands.Bot = bot

    @app_commands.command(name="allow_notify", description="Permite que el bot le notifique al usuario cuando estés en un voice.")
    @app_commands.describe(user="Usuario al cual le permites saber si te conectaste a un voice.")
    async def allow_notify(self, interaction: discord.Interaction, user: discord.Member):
        user = get_user(user.id)
        if not user:
            return await interaction.response.send_message("Tú usuario no existe en la base de datos, para que el bot pueda saber ")
        if user.bot:
            return await interaction.response.send_message("No se puede agregar un bot.")
        if user.id == interaction.user.id:
            return await interaction.response.send_message("No te puedes agregar a ti mismo.")
        embed = Embed()
        embed.set_author(name="Configuración de notificaciones", icon_url=self.bot.user.display_avatar.url)
        embed.description = f"Al aceptar, le estás dando permiso a {self.bot.user.mention} para que le notifique a {user.mention} cuando estés en un voice, cuando cambie tu estado de actividad y cuando te conectes y desconectes de Discord.\n"
        embed.set_footer(text="Si quieres quitarle el permiso, usa el comando /deny")
        embed.color = Colour.blue()
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Usuario", value=f"{user.mention}", inline=True)
        return await interaction.response.send_message(embed=embed, view=UserNotifyView(user=user), ephemeral=True)
    
    @app_commands.command(name="deny", description="Elimias el permiso de notificarte a un usuario.")
    @app_commands.describe(user="Usuario al cual le quitas el permiso de notificarte.")
    async def deny(self, interaction: discord.Interaction, user: discord.Member):
        if user.bot:
            return await interaction.response.send_message("En serio?")
        if user.id == interaction.user.id:
            return await interaction.response.send_message("Esto no tiene sentido, no crees?")
        try:
            update_user_notify_list(interaction.user.id, user.id, False)
        except UserNotFound as error:
            return await interaction.response.send_message("Tu usuario no existe en la base de datos. Si quieres crear el usuario usa el comando /inituser", ephemeral=True)
