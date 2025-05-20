import discord
import discord.ext.commands
from utils.mongo_utils import get_user
class ServerEvents(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
    
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
    