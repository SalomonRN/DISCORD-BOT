import discord
from utils.errors import UserNotFound
from utils.mongo_utils import update_user_notify_list

# Modal -> Un formulario
# https://www.youtube.com/watch?v=PRC4Ev5TJwc
class Questionnaire(discord.ui.Modal, title='Lo que sale arriba'):
    name = discord.ui.TextInput(label='Name')
    answer = discord.ui.TextInput(label='Answer', style=discord.TextStyle.paragraph)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your response, {self.name}!', ephemeral=True)
        
    async def on_error(self, interaction: discord.Interaction, error):
        print("ERROR-----", error)


class UserNotifyView(discord.ui.View):
    
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
    
    @discord.ui.button(label='Aceptar', style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            updated = update_user_notify_list(interaction.user.id, self.user.id, add=True)
            
            if not updated:
                return await interaction.response.send_message("El usuario ya se encuentra en la lista de gente a notificar.", ephemeral=True)

            return await interaction.response.send_message(f"El usuario {self.user.mention} fue agregado a lista de gente a notificar.", ephemeral=True)
        except UserNotFound as error:
            return await interaction.response.send_message("Tu usuario no existe en la base de datos. Si quieres crear el usuario usa el comando /inituser", ephemeral=True)

    @discord.ui.button(label='Rechazar', style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        # return await interaction.response.send_message(f"Ningún cambio!", ephemeral=True)
        update_user_notify_list(interaction.user.id, self.user.id, add=False)
        return await interaction.response.send_message(f"El usuario {self.user.mention} fue eliminado de la lista de gente a notificar.", ephemeral=True)
    
class UserCreateView(discord.ui.View):
    
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
    
    @discord.ui.button(label='Aceptar', style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Questionnaire())
    
    @discord.ui.button(label='Rechazar', style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        return await interaction.response.send_message(f"Ningún cambio!", ephemeral=True)