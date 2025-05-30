import re
import os
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
from dotenv import load_dotenv
from utils.utils import create_audio
load_dotenv()

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
async def message(ctx: discord.ext.commands.Context):
    if len(ctx.message.content.split(" ")) == 1:
        embed = discord.Embed(colour=0x043548)
        embed.title ="📢 Cómo usar el comando message"
        embed.description= "¿Quieres que el bot hable por ti en un canal de voz sin unirte ¡Este comando es para ti!\n🔧 Recuerda que el prefijo por defecto es >, aunque puede variar según el servidor.\n\n🔸 Enviar un mensaje a otro usuario en un canal de voz:\n** >message @usuario Tu mensaje **\n  ➡️ El mensaje será enviado al canal de voz donde se encuentre el usuario mencionado.\n  ⚠️ Asegúrate de que el usuario esté conectado a un canal de voz en el mismo servidor.\n\n🔸 Enviar un mensaje en tu canal de voz actual:\n*** >message Tu mensaje ***\n  ➡️ El bot dirá tu mensaje en el canal de voz en el que te encuentres actualmente.\n  ⚠️ Debes estar conectado a un canal de voz para usar esta opción."
        return await ctx.send(embed=embed, ephemeral=True)
    try:
        vc = None
        flag = False
        # Si esto se cumple, significa que el mensaje tiene un usuario mencionado, por lo que se enviará el mensaje a ese usuario
        if re.match(r"<@\d+[0-9]>", ctx.message.content.split(" ", 2)[1]):
            if not ctx.message.mentions[0].voice:
                return await ctx.send("Por favor menciona a un usuario que esté en un canal de voz.", ephemeral=True)
            
            vc = ctx.message.mentions[0].voice.channel
            flag = True
        # Si no mencionó a nadie, pero el autor del comando está en un canal de voz
        elif not ctx.author.voice:
            # Si el autor del comando no está en un canal de voz, envía un mensaje de error
            return await ctx.send("Por favor menciona a un usuario que esté en un canal de voz o únete a uno.", ephemeral=True)
        else:
            vc = ctx.author.voice.channel
        
        bot_vc = ctx.voice_client
        
        if not bot_vc:
            bot_vc = await vc.connect()
        
        elif bot_vc.channel != vc:
            await bot_vc.move_to(vc)
        
        list_users = re.findall(r"<@\d+[0-9]>", ctx.message.content)

        for user in list_users:
            ctx.message.content = ctx.message.content.replace(user, bot.get_user(int(user[2:-1])).name)
        
        if flag:
            message = ctx.message.content.split(" ", 2)[2]
        else:
            message = ctx.message.content.split(" ", 1)[1]
        
        file_name = create_audio(message)
        if not os.path.exists(file_name):
            return await ctx.send("No pude crear el audio, revisa el mensaje que enviaste.", ephemeral=True)
        
        bot_vc.play(discord.FFmpegPCMAudio(file_name))
    except Exception as e:
        print(f"Error al conectar al canal de voz: {e}")
        return await ctx.send("Algo salió mal...", ephemeral=True)

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
    # await bot.add_cog(UserEvents(bot))
    # await bot.add_cog(ServerEvents(bot))
    await bot.add_cog(CommandsBot(bot))
    await bot.add_cog(NotifyCommands(bot))
    # await bot.add_cog(LogCommands(bot))
    await bot.start(TOKEN)

# await bot.run(TOKEN)
asyncio.run(main())
