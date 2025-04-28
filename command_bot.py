import datetime
import discord
from discord import Colour, app_commands
from discord.embeds import Embed
from typing import Literal, Any, List
import discord.ext
import discord.ext.commands
from utils import create_user_in_db, get_advice, create_server_in_db, server_exist, change_active_status_user, delete_server_data, change_active_status, update_server_info, create_event
from web_scrapping.valo_scrapping import search

class CommandsBot(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot, DEBUG: bool):
        self.bot: discord.ext.commands.Bot = bot
        self.DEBUG = DEBUG
          
    @app_commands.command(name="create_rol", description="Crea el rol que quieras")
    @app_commands.describe(name="El nombre del rol que quieres crear")
    async def create_rol(self, interaction: discord.Interaction, name: str):
        if not self.DEBUG:
            return await interaction.response.send_message("Este comando no está finalizado y no lo quiero quitar :)", 
                                                           ephemeral=True, delete_after=2)
        print(interaction.user.resolved_permissions.manage_roles)
        await interaction.guild.create_role(name=name)
        await interaction.response.send_message("Rol creado")        
    
    @app_commands.command()
    async def join(self, interaction: discord.Interaction):
        if not self.DEBUG:
            return await interaction.response.send_message("Este comando no está finalizado y no lo quiero quitar :)", 
                                                           ephemeral=True, delete_after=2)
        
        if interaction.user.voice is None:
            await interaction.response.send_message("No estas en un canal de voz")

        channel = interaction.user.voice.channel
        await channel.connect()

    @app_commands.command(description="Envía un mensaje al voice que tú quieras sin la necesidad de entrar 😉")
    async def message(self, interaction: discord.Interaction):
        if not self.DEBUG:
            return await interaction.response.send_message("Este comando no está finalizado y no lo quiero quitar :)", 
                                                           ephemeral=True, delete_after=2)        
        channel = self.bot.get_channel(795858207653232643)
        print(isinstance(channel, discord.VoiceChannel))
        
        await channel.connect()

    @app_commands.command(description="Muestra que y quienes están jugando algo ahorita.")
    async def games(self, interaction: discord.Interaction):
        if not interaction.user.resolved_permissions.administrator:
            return await interaction.response.send_message("No tienes permisos para ejecutar este comando", 
                                                           ephemeral=True, delete_after=2)
        
        if not self.DEBUG:
            from time import sleep
            await interaction.response.send_message("Este comando no está aún bien hecho, así que puede dar errores, tales como no hacer nada o explotar la Luna, tenlo presente.", ephemeral=True, delete_after=3)
            await sleep(5)
        
        users = [user for user in interaction.guild.members if not user.bot and user.activity]
        if not users:
            return await interaction.response.send_message("Parece que nadie está jugando algo...", ephemeral=True, delete_after=3)
        
        for user in users:
            if user.activity.type == discord.ActivityType.playing:
                await interaction.response.send_message(f"{user.name} está jugando actualmente {user.activity.name}", ephemeral=True)
        
    @app_commands.command(description="Comando para ver si tienes permisos de admin.")
    async def perms(self, interaction: discord.Interaction):
        if not interaction.user.resolved_permissions.administrator:
            return await interaction.response.send_message('No tienes permisos para ejecutar comandos "avanzados"', ephemeral=True)
        return await interaction.response.send_message('SI tienes permisos para ejecutar comandos "avanzados"', ephemeral=True)      
        
    @app_commands.command(description="Es un secreto 🤫")
    async def init_users(self, interaction: discord.Interaction):
        """ Inicializa los usuarios en la base de datos """
        if not interaction.user.resolved_permissions.administrator:
            return await interaction.response.send_message('NO tienes permisos para ejecutar este comando', ephemeral=True)
        
        members = [member for member in interaction.guild.members if not member.bot]
        for user in members:
            create_user_in_db(user)
        return await interaction.response.send_message('Parece que ya.', ephemeral=True)

    @app_commands.command(name="ping", description="Responde con un pong")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="hola", description="Saluda al bot")
    async def hola(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"¡Hola {interaction.user.mention}!")

    @app_commands.command(name="valoinfo", description="Busca tus estadísticas de valorant 😊")
    @app_commands.describe(username="Tu Riot ID, incluye el tagline, o sea el #", game="Elige un tipo de juego para buscar tus estadísticas")
    async def valoinfo(self, interaction: discord.Interaction, username: str, game: Literal["competitive", "all", "unrated"]):
        if not self.DEBUG:
            return await interaction.response.send_message('Lastimosamente el servidor gratuito donde está hospedado el bot no permite usar ciertas herramientas para usar este comando, y no tengo como para alquilar uno.', ephemeral=True, delete_after=10)
        
        await interaction.response.send_message(f"⏳ Buscando información de {username} en {game} esto puede tardar unos segundos o minutos...", ephemeral=True, delete_after=8.0)
        
        # await interaction.response.defer() 
            
        stats = await search(f"https://valorant.op.gg/profile/{username.replace("#", "-")}?statQueueId={game}")
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
                        Estadísticas de {username} en {game},
                        Rango: {stats[0].get("range")}
                        KDA: {stats[0].get("kda")}
                        % tiro a la cabeza {stats[0].get("head_shot")}
                        % tiro al cuerpo {stats[0].get("body_shot")}
                        % tiro a las piernas {stats[0].get("legs_shot")}
                        Daño por ronda: {stats[0].get("damage_round")}
                        Win Rate: {stats[0].get("win_rate")}
                        
                        ROLES
                        {stats_roles}
                        """,
                        color=discord.Color.blue())
            await interaction.followup.send(embed=embed)
            
    @app_commands.command(name="change_notify", description="Cambia el estado de las notificaciones cuando juegas")
    async def change_notify(self, interaction: discord.Interaction):
        await interaction.response.send_message("Este comando no está aún bien hecho, así que puede dar errores, tales como no hacer nada o explotar el Sol, tenlo presente.", ephemeral=True, delete_after=5)
        if interaction.user.bot: return
        
        notify = change_active_status_user(interaction.user.id)
        
        await interaction.response.send_message(f"Se ha cambiado a un estado de {'SI' if notify else 'NO'} permitir notificaciones", ephemeral=True, delete_after=1.5)

    @app_commands.command(name="advice", description="Te da un consejo totalmente random. La traducción es hecha por google translate, y no es exacta.")
    async def advice(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Y el consejo es...", ephemeral=True, delete_after=1.8)
        advice = await get_advice()
        return await interaction.followup.send(advice)
        
        
    @app_commands.command(name="event", description="Crea un evento de reunion.")
    @app_commands.describe(title="Titulo del evento",
                           date="Fecha del evento. (Formato DD-MM-YYYY)", time="Hora del evento. (Formato HH:MM y de 24 Horas)",
                           users="Lista de usuarios, separados por coma (@Usuario1, @Usuario2, @Usuario3)")
    async def event(self, interaction: discord.Interaction, title: str, date: str, time: str, users:str):
        try:
            users_l = [int(user[2:-1]) for user in list(map(lambda x: x.replace(" ", ""), users.split(',')))]
        except Exception as error:
            if isinstance(error, ValueError):
                return await interaction.response.send_message("ASEGURATE DE AGREGAR BIEN LAS COMAS")
            return await interaction.response.send_message("Está todo bien escrito?")
        
        for id_user in users_l:
            user = interaction.guild.get_member(id_user)
            if user.bot:
                return await interaction.response.send_message("NO PUEDES AGREGAR BOTS AL EVENTO")

        if interaction.user.id not in users_l: 
            users_l.append(interaction.user.id) 
                
        try:
            date = datetime.datetime.strptime(f"{date} {time}", "%d-%m-%Y %H:%M")
        except Exception as e:
            return await interaction.response.send_message("ERROR. Seguro que la fecha y hora está bien escrita?", delete_after=3.0, ephemeral=True)
            
        if date <= datetime.datetime.now():
            return await interaction.response.send_message("La fecha y hora no pueden ser pasadas")
        create_event(interaction.user.name, title, date, interaction.guild_id, users_l)
        await interaction.response.send_message(f"Evento creado {title}, fecha {date}")

    @app_commands.command(name="link", description="Link directo al repositorio del proyecto en GitHub 😊")
    async def git_hub(self, interaction: discord.Interaction):
        embed = Embed(
            color=Colour.blue(),
            title="DISCORD-BOT",
            description=(
                "Aquí tienes el enlace directo al código del bot. Si quieres echar un vistazo para ver cómo funciona, adelante.\n" 
                "Si detectas algún error, te agradecería que crearas un nuevo *Issue* en la página. " 
                "También, si tienes ideas para mejorar el bot, puedes enviar un *Pull Request* y con gusto lo revisaré 😊.\n\n"
                "¡Siéntete libre de usar este bot como gustes!")
        )
        embed.set_author(
            name="SaloBot",
            icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS8paEvGt3sACXnfgr_NPr010dg0uFjtXZBbQ&s",
        )
        embed.set_footer(text="Hecho por Salomón RN")
        embed.add_field(name="🔗 Enlace al Código", value="[Ver en GitHub](https://github.com/SalomonRN/DISCORD-BOT)", inline=False)
        await interaction.response.send_message(embed=embed)