import discord
import discord.ext
import discord.ext.commands
from utils.mongo_utils import user_exist, create_user_in_db, get_user, get_server

class UserEvents(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
    
    @discord.ext.commands.Cog.listener()
    async def on_message(self, message: discord.message.Message):
        """ Evento que se ejecuta cuando se recibe cualquier mensaje """

        message.content = message.content.lower()
        
        if message.author == self.bot.user:
            return
        # Ayuda para el usuario que no sabe el prefijo
        if message.content.startswith('prefix'):
            await message.channel.send("El prefijo para mis comandos es: " + self.bot.command_prefix)
        return await self.bot.process_commands(message)
    
    # @discord.ext.commands.Cog.listener()
    # async def on_member_join(self, member: discord.member.Member):
    #     """ Evento que se ejecuta cuando un usuario entra al servidor """
    #     await member.create_dm()
    #     # AGREGAR MAS INFO ACÁ
    #     await member.dm_channel.send(
    #         f'Hola {member.name}, bienvenido a mi servidor! {member.guild.name}, usa {self.bot.command_prefix}notify para habilitar o deshabilitar las notificaciones cuando juegas'
    #     )
 
    #     if not user_exist(member.id):
    #         create_user_in_db(member)

    @discord.ext.commands.Cog.listener()
    async def on_member_remove(self, member: discord.member.Member):
        pass

    # @discord.ext.commands.Cog.listener()
    # async def on_invite_create(self, invite: discord.invite.Invite):
    #     """ Evento que se ejecuta cuando se crea una invitacion """
    #     server = get_server(invite.guild.id)
    #     channel_id = server.get('admin_channel')
    #     if not channel_id: 
    #         await invite.guild.owner.create_dm()
    #         return await invite.guild.owner.dm_channel.send(f"DEBES CONFIGURAR EL CANAL DE LOGS EN TU SERVER {invite.guild.name}")
    #     channel = self.guild.get_channel(int(channel_id))
    #     await channel.send(f"{invite.inviter} creó una invitacion {invite.url}, se invitó a: {invite.target_user}")

    # @discord.ext.commands.Cog.listener()
    # async def on_presence_update(self, before: discord.Member, after: discord.Member):
    #     #
    #     """ Evento que se ejecuta cuando un usuario cambia su estado """
        
    #     if before.bot: return
        
    #     user: dict = get_user(after.id)
    #     if not user:
    #         return
        
    #     server = get_server(before.guild.id)        
    #     channel_noti = server.get('notify_channel')
        
    #     if not channel_noti:
    #         await before.guild.owner.create_dm()
    #         return await before.guild.owner.dm_channel.send(f"DEBES CONFIGURAR PARA LAS NOTI EN EN TU SERVER {before.guild.name}")       
    #     channel =  before.guild.get_channel(channel_noti)

    #     # Verifica si el usuario tiene actividad, y si esa actividad es de un juego
    #     if after.activity and after.activity.type == discord.ActivityType.playing:
    #         if after.activity.name == before.activity.name:
    #             return
    #         if not user.get('notify', False):
    #             return await channel.send(f"{after.name} no tiene la opcion de Notificar cuando juega :c")    
    #         return await channel.send(f"{after.name} está jugando actualmente {after.activity.name}")
