import asyncio
import discord
from tasks.event_task import EventTask
from discord.ext import commands
import discord.ext
import discord.ext.commands
from os import getenv
import utils.mongo as mongo
from cogs.user_events import UserEvents
from cogs.command_bot import CommandsBot
from utils.mongo_utils import server_exist, create_server_in_db, change_active_status, update_server_info, delete_server_data
from discord import app_commands

TOKEN = getenv("DISCORD_TOKEN")
APP_ID = getenv("APP_ID")
PUBLIC_KEY = getenv("PUBLIC_KEY")
MY_SERVER_ID = getenv("MY_SERVER_ID")
DEBUG = bool(getenv("DEBUG", False))
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
    if not ctx.author.resolved_permissions.administrator:
        return
    
    bot.command_prefix = ctx.message.content.split(" ")[1]
    await ctx.send("Prefijo cambiado a: " + bot.command_prefix)


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
    await bot.add_cog(CommandsBot(bot, DEBUG))
    await bot.start(TOKEN)

# await bot.run(TOKEN)
asyncio.run(main())
