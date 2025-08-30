import asyncio
import discord
import discord.ext
import discord.ext.commands
from cogs.commands import CommandsBot, NotifyCommands, YouTubeCog, SpeakCog, LogCommands
from tasks.event_task import EventTask
from discord.ext import commands
from core.db.servers.mongo import server_exist, create_server_in_db, update_server_info, change_server_status
from core.db import client

from os import getenv
from dotenv import load_dotenv
load_dotenv()

TOKEN = getenv("DISCORD_TOKEN")
APP_ID = getenv("APP_ID")
PUBLIC_KEY = getenv("PUBLIC_KEY")
MY_SERVER_ID = getenv("MY_SERVER_ID")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='sb>',intents=intents)

@bot.event
async def on_connect():
    print("ON CONNECT")

@bot.event
async def on_ready():
    MAIN_GUILD = bot.get_guild(int(MY_SERVER_ID)) # El id de mi servidor
    # mongo.init_connection()
    await setup()
    
    synced = await bot.tree.sync()  # Sincroniza los comandos de barra
    
    print(f"Se sincronizaron {len(synced)} comandos de barra!")
    print(f'We have logged in as {bot.user}')
    await MAIN_GUILD.get_channel(802609235912949810).send("Bot funcionando :)")


@bot.command()
async def change(ctx: discord.ext.commands.Context):
    if not await bot.is_owner(ctx.author):
        return
    else:
        activity = " ".join(ctx.message.content.split(" ")[2:]).capitalize()
        match(ctx.message.content.split(" ")[1]):
            case "play":       
                game = discord.Game(name=activity)
                await bot.change_presence(activity=game)
            case "stream":
                activity = " ".join(ctx.message.content.split(" ")[2:-1])
                url = ctx.message.content.split(" ")[-1]
                if url.islower():
                    return await ctx.send("Vuelva a mandar el comando :), pero si ya cambió la actividad del bot ignora esto.", ephemeral=True)
                await bot.change_presence(activity=discord.Streaming(name=activity, url=url))
            case "listen":
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity))
            case "watch":
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))
            case _:
                await ctx.send("Algo salió mal...")
        

        
        
async def setup():
    await client.ping_db() # Test connection
     
    await bot.add_cog(CommandsBot(bot))
    await bot.add_cog(YouTubeCog(bot))
    await bot.add_cog(NotifyCommands(bot))
    await bot.add_cog(LogCommands(bot))
    await bot.add_cog(EventTask(bot))
    await bot.add_cog(SpeakCog(bot))  

async def main():
    await bot.start(TOKEN)

# await bot.run(TOKEN)
if __name__ == "__main__":
    asyncio.run(main())
