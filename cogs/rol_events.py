import discord
import discord.ext
import discord.ext.commands

class RolEvents():
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
    
    @discord.ext.commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.role.Role):
        print(role.created_at)
        print(type(role))

    @discord.ext.commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.role.Role):
        print(role)
        print(type(role))
