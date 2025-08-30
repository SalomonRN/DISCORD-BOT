import discord
import discord.ext.commands
from core.db.servers.mongo import update_server_info, change_server_status, server_exist, create_server_in_db
from core.db.users.mongo import get_user

class ServerEvents(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @discord.ext.commands.Cog.listener()
    async def on_guild_join(guild: discord.Guild):
        """ Cuando el bot entra a un servidor """
        if not server_exist(guild.id):
            create_server_in_db(guild)
            
        await guild.owner.create_dm()
        await guild.owner.dm_channel.send("Gracias por agregar el bot. ")
    
    @discord.ext.commands.Cog.listener()
    async def on_guild_update(before: discord.Guild, after: discord.Guild):
        """ Cuando un servidor es actualizado, mas que todo el nombre """
        pass
        if before.name != after.name:
            update_server_info(after)
    
    @discord.ext.commands.Cog.listener()
    async def on_guild_remove(guild: discord.Guild):
        """ Cuando el bot sale de un servidor """
        change_server_status(guild.id)

    @discord.ext.commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        
        user = get_user(member.id)
       
        if not user:
            return
        
        if before.channel == after.channel:
            return

        if not after.channel:
            return
        
        if before.channel and after.channel and before.channel.guild == after.channel.guild:
            return
        
        try:        
            for user_id in user.get('notify_to', []):
                dm = await self.bot.create_dm(self.bot.get_user(int(user_id)))
                await dm.send(f"Ey, tu amig@ {member.name} está en {after.channel.name} en {member.guild.name}, y si te unes?")
        except Exception as error:
            # IMPLEMENTAR LOGICA DE LOGS
            pass
    