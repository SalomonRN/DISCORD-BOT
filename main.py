import asyncio
import discord
from cogs.commands.logs_commands import LogCommands
from cogs.commands.notify_commands import NotifyCommands
from tasks.event_task import EventTask
from discord.ext import commands
import discord.ext
import discord.ext.commands
from os import getenv
import utils.mongo as mongo
from cogs.events.user_events import UserEvents
from cogs.commands.command_bot import CommandsBot
from cogs.events.server_events import ServerEvents
from utils.mongo_utils import server_exist, create_server_in_db, change_active_status, update_server_info, delete_server_data
from discord import app_commands

TOKEN = getenv("DISCORD_TOKEN")
APP_ID = getenv("APP_ID")
PUBLIC_KEY = getenv("PUBLIC_KEY")
MY_SERVER_ID = getenv("MY_SERVER_ID")
MAIN_GUILD = None

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='>',intents=intents)

@bot.event
async def on_connect():
    print("ON CONNECT")

@bot.event
async def on_ready():
    global MAIN_GUILD
    MAIN_GUILD = bot.get_guild(int(MY_SERVER_ID)) # El id de mi servidor
    mongo.init_connection()
    synced = await bot.tree.sync()  # Sincroniza los comandos de barra
    
    print(f"Se sincronizaron {len(synced)} comandos de barra!")
    print(f'We have logged in as {bot.user}')
    await bot.add_cog(EventTask(bot))

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
                print("ALGO MALIO SAL")  
        
@bot.event
async def on_guild_join(guild: discord.Guild):
    """ Cuando el bot entra a un servidor """
    if not server_exist(guild.id):
        create_server_in_db(guild)
    else:
        change_active_status(guild.id)
        
    await guild.owner.create_dm()
    await guild.owner.dm_channel.send("Gracias por agregar el bot. ")
        
@bot.event
async def on_guild_remove(guild: discord.Guild):
    """ Cuando el bot sale de un servidor """
    delete_server_data(guild.id)
    change_active_status(guild.id)

@bot.event
async def on_guild_update(before: discord.Guild, after: discord.Guild):
    """ Cuando un servidor es actualizado, mas que todo el nombre """
    pass
    if before.name != after.name:
        update_server_info(after)
        
async def main():
    await bot.add_cog(UserEvents(bot))
    await bot.add_cog(ServerEvents(bot))
    await bot.add_cog(CommandsBot(bot))
    await bot.add_cog(NotifyCommands(bot))
    await bot.add_cog(LogCommands(bot))
    await bot.start(TOKEN)

# await bot.run(TOKEN)
asyncio.run(main())
