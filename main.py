from discord.embeds import Embed
from discord import app_commands
from typing import Literal
import asyncio
import discord
from task import Task
from discord.ext import commands
import discord.ext
import discord.ext.commands
from os import getenv
import mongo
from utils import create_user_in_db, get_advice, create_server_in_db, server_exist, change_active_status_user, delete_server_data, change_active_status, update_server_info
from events import UserEvents
from web_scrapping.valo_scrapping import search

TOKEN = getenv("DISCORD_TOKEN")
APP_ID = getenv("APP_ID")
PUBLIC_KEY = getenv("PUBLIC_KEY")
MY_SERVER_ID = getenv("MY_SERVER_ID")

MAIN_GUILD = None
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='>',intents=intents)
user_event = None

@bot.event
async def on_ready():
    global MAIN_GUILD
    MAIN_GUILD = bot.get_guild(int(MY_SERVER_ID)) # El id de mi servidor
    mongo.init_connection()
    user_event.guild = MAIN_GUILD    
    synced = await bot.tree.sync()  # Sincroniza los comandos de barra
    
    print(f"Se sincronizaron {len(synced)} comandos de barra!")
    print(f'We have logged in as {bot.user}')
    
    # ESTO SOLO ES PARA MI SERVIDOR
    await MAIN_GUILD.get_channel(802609235912949810).send("Bot funcionando :)")

@bot.command()
async def change(ctx: discord.ext.commands.Context):
    if not ctx.author.resolved_permissions.administrator:
        return
    
    bot.command_prefix = ctx.message.content.split(" ")[1]
    await ctx.send("Prefijo cambiado a: " + bot.command_prefix)


  
# @bot.command()
# async def join(ctx: discord.ext.commands.context.Context):
    
#     if ctx.author.voice is None:
#         await ctx.send("No estas en un canal de voz")

#     channel = ctx.author.voice.channel
#     await channel.connect()

# @commands.hybrid_command()
# async def create_rol(ctx: discord.ext.commands.context.Context, member, reason, days):
#     await MAIN_GUILD.create_role(name="".join(ctx.message.content.split(" ")[1:]))
#     await ctx.send("Rol creado")
    
# @bot.command()
# async def message(ctx: discord.ext.commands.context.Context):
#     bot
#     channel = bot.get_channel(795858207653232643)
#     print(isinstance(channel, discord.VoiceChannel))
    
#     await channel.connect()

@bot.command()
async def games(ctx: discord.ext.commands.context.Context):
    if not ctx.author.resolved_permissions.administrator:
        return await ctx.send("No tienes permisos para ejecutar este comando")
    
    users = [user for user in ctx.guild.members if not user.bot]
    for user in users:
        if not user.activity: continue
        if user.activity.type == discord.ActivityType.playing:
            await ctx.send(f"{user.name} está jugando actualmente {user.activity.name}")

@bot.command()
async def perm(ctx: discord.ext.commands.context.Context):
    if not ctx.author.resolved_permissions.administrator:
        return await ctx.send("No tienes permisos para ejecutar este comando")
    
@bot.command()
async def init_users(ctx: discord.ext.commands.context.Context):
    """ Inicializa los usuarios en la base de datos """
    if not ctx.author.resolved_permissions.administrator:
        return
    
    members = [member for member in MAIN_GUILD.members if not member.bot]
    for user in members:
        create_user_in_db(user)

@bot.event
async def on_guild_join(guild: discord.Guild):
    """ Cuando el bot entra a un servidor """
    if not server_exist(guild.id):
        create_server_in_db(guild)
    else:
        change_active_status(guild.id)
        
    await guild.owner.create_dm()
    await guild.owner.dm_channel.send("ASI FUNCIONA EL BOT....")

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


# COMANDOS DE BARRA 
@bot.tree.command(name="ping", description="Responde con un pong")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@bot.tree.command(name="hola", description="Saluda al bot")
async def hola(interaction: discord.Interaction):
    await interaction.response.send_message(f"¡Hola {interaction.user.mention}!")

@bot.tree.command(name="valoinfo", description="Busca tus estadísticas de valorant 😊")
@app_commands.describe(username="Tu Riot ID, incluye el tagline, o sea el #", type="Elige un tipo de juego para buscar tus estadísticas")
async def valoinfo(interaction: discord.Interaction, username: str, type: Literal["competitive", "all", "unrated"]):
    await interaction.response.send_message(f"⏳ Buscando información de {username} en {type} esto puede tardar unos segundos o minutos...", ephemeral=True)
    
    # await interaction.response.defer() 
        
    stats = await search(f"https://valorant.op.gg/profile/{username.replace("#", "-")}?statQueueId={type}")
    if isinstance(stats, str):
        return await interaction.followup.send("Ups,", stats.lower())
    else:
        stats_roles = ""
        for rol in stats[1]: 
            stats_roles += f"""
            Rol: {rol.get("rol_name")}
            Pick Rate: {rol.get("pick_rate")}
            KDA: {rol.get("kda")}
            Winrate: {rol.get("winrate")}
            """
                        
        embed = Embed(title=f"Estadísticas de {username}",
                    description=f"""
                    Estadísticas de {username} en {type},
                    Rango: {stats[0].get("range")}
                    KDA: {stats[0].get("kda")}
                    % tiro a la cabeza {stats[0].get("head_shot")}
                    % tiro al cuerpo {stats[0].get("body_shot")}
                    % tiro a las piernas{stats[0].get("legs_shot")}
                    Daño por ronda: {stats[0].get("damage_round")}
                    Win Rate: {stats[0].get("win_rate")}
                    
                    ROLES
                    {stats_roles}
                    """,
                    color=discord.Color.blue())
        await interaction.followup.send(embed=embed)
        
@bot.tree.command(name="change_notify", description="Cambia el estado de las notificaciones cuando juegas")
async def change_notify(interaction: discord.Interaction):
    if interaction.user.bot: return
    
    notify = change_active_status_user(interaction.user.id)
    
    await interaction.response.send_message(f"Se ha cambiado a un estado de {"SI" if notify else 'NO'} permitir notificaciones", ephemeral=True)

@bot.tree.command(name="advice", description="Te da un consejo totalmente random. La traducción es hecha por google translate, y no es exacta.")
async def advice(interaction: discord.Interaction):
    await interaction.response.send_message(get_advice())

async def main():
    global user_event
    user_event = UserEvents(bot)
    await bot.add_cog(user_event)
    await bot.start(TOKEN)

# await bot.run(TOKEN)
asyncio.run(main())
