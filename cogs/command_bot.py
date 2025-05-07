import os
import datetime
import asyncio
import discord
from discord import Colour, app_commands
from discord.embeds import Embed
from typing import Literal
import discord.ext
import discord.ext.commands
from utils.mongo_utils import create_user_in_db, change_active_status_user, create_event, create_log_bug
from utils.utils import get_advice, create_audio
from utils.web_scrapping.valo_scrapping import search

class CommandsBot(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot, DEBUG: bool):
        self.bot: discord.ext.commands.Bot = bot
        self.DEBUG = DEBUG
          
    @app_commands.command(name="ping", description="Responde con un pong")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! ms{round(self.bot.latency, 1)}")
        
    @app_commands.command(name="hola", description="Saluda al bot")
    async def hola(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"¡Hola {interaction.user.mention}!")
    
    @app_commands.command(name="advice", description="Te da un consejo totalmente random. La traducción es hecha por google translate, y no es exacta.")
    async def advice(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Y el consejo es...", ephemeral=True, delete_after=1.8)
        advice = await get_advice()
        return await interaction.followup.send(advice)
    
    @app_commands.command(description="Envía un mensaje al voice que tú quieras sin la necesidad de entrar 😉")
    @app_commands.describe(message="Mensaje que quieres que diga el bot.", voice="Voice al que va a entrar el bot.")
    async def message(self, interaction: discord.Interaction, message: str, voice: discord.VoiceChannel):
        await interaction.response.defer(ephemeral=True)
        print("🔊 Preparando mensaje de voz...")

        if "<@" in message:
            print("⚠️ Mensaje con mención detectado")

        # file_name = create_audio(message)
        file_name = "voz.mp3"
        if not file_name:
            return await interaction.followup.send( "⚠️ Ocurrió un error al generar el audio. Intenta de nuevo sin emojis o caracteres especiales.", ephemeral=True)

        try:
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.disconnect(force=True)
            
            bot_vc = interaction.guild.voice_client
            
            if not bot_vc:
                discord.opus.load_opus("./bin/libopus.dll") 
                try:
                    print("🔌 Conectando al canal de voz...")
                    bot_vc = await voice.connect()
                    print("🔌 Conectado al canal de voz!!!!!!!!!!!")
                except Exception as error:
                    print("❌ ERROR*---*-*-*--:", error)

                
                print("🔌 Conectando al canal...")
                print("🤖 Bot VC:", bot_vc)
                print("🎙 Voice Channel:", voice.name, voice.id)
                print("🎛 Voice Permissions:", voice.permissions_for(interaction.guild.me))
                print("Opus loaded:", discord.opus.is_loaded())
            elif bot_vc.channel != voice:
                print("🔁 Moviendo a otro canal...")
                await bot_vc.move_to(voice)

            # Detener si está reproduciendo
            if bot_vc.is_playing():
                bot_vc.stop()

            # Reproducir el audio
            audio = discord.FFmpegPCMAudio(file_name)
            bot_vc.play(audio, after=lambda e: print("✅ Reproducción terminada." if not e else f"❌ Error al reproducir: {e}"))

            print("🎶 Reproduciendo...")
            await interaction.followup.send(f"✅ Reproduciendo mensaje en **{voice.name}**.")

            # Esperar a que termine
            while bot_vc.is_playing():
                await asyncio.sleep(1)

            await bot_vc.disconnect()
            os.remove(file_name)
            print("🧹 Limpieza completada")

        except discord.ClientException as e:
            print("⚠️ ClientException:", e)
            return await interaction.followup.send("⚠️ Error de cliente Discord. Código: 1", ephemeral=True)
        except asyncio.TimeoutError:
            print("⚠️ Timeout al conectar.")
            return await interaction.followup.send("⚠️ Timeout al conectar. Código: 2", ephemeral=True)
        except discord.opus.OpusNotLoaded:
            print("⚠️ Opus no cargado.")
            return await interaction.followup.send("⚠️ La librería Opus no está cargada. Código: 3", ephemeral=True)
        except Exception as error:
            print("❌ ERROR:", error)
            return await interaction.followup.send("⚠️ Error inesperado. Código: 0000000", ephemeral=True)
        

    @app_commands.command(description="Muestra qué y quiénes están jugando algo ahora mismo.")
    async def games(self, interaction: discord.Interaction):

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("No tienes permisos para ejecutar este comando.",
                                                           ephemeral=True, delete_after=4)

        if not self.DEBUG:
            await interaction.response.send_message("Este comando aún está en desarrollo. Puede tener errores impredecibles.",
                                                    ephemeral=True, delete_after=5)
            await asyncio.sleep(1)

        jugadores = [
            f"{member.display_name} está jugando {member.activity.name}"
            for member in interaction.guild.members
            if not member.bot and member.activity and member.activity.type == discord.ActivityType.playing
        ]

        send = ( interaction.followup.send if interaction.response.is_done() else interaction.response.send_message )

        if not jugadores:
            return await send("Parece que nadie está jugando algo...", ephemeral=True, delete_after=4)

        mensaje = "\n".join(jugadores)
        await send(mensaje, ephemeral=True)

    @app_commands.command(description="Comando para ver si tienes permisos de admin.")
    async def perms(self, interaction: discord.Interaction):
        if not interaction.user.resolved_permissions.administrator:
            return await interaction.response.send_message('No tienes permisos para ejecutar comandos "avanzados"', ephemeral=True)
        return await interaction.response.send_message('SI tienes permisos para ejecutar comandos "avanzados"', ephemeral=True)      
        
    # ToDo MEJOR POR PREFIJO??
    @app_commands.command(description="Es un secreto 🤫")
    async def init_users(self, interaction: discord.Interaction):
        """ Inicializa los usuarios en la base de datos """
        if not interaction.user.resolved_permissions.administrator:
            return await interaction.response.send_message('NO tienes permisos para ejecutar este comando', ephemeral=True)
        
        members = [member for member in interaction.guild.members if not member.bot]
        for user in members:
            create_user_in_db(user)
        return await interaction.response.send_message('Parece que ya.', ephemeral=True)

    @app_commands.command(name="change_notify", description="Cambia el estado de las notificaciones cuando juegas")
    async def change_notify(self, interaction: discord.Interaction):
        await interaction.response.send_message("Este comando no está aún bien hecho, así que puede dar errores, tales como no hacer nada o explotar el Sol, tenlo presente.", ephemeral=True, delete_after=5)
        if interaction.user.bot: return
        
        notify = change_active_status_user(interaction.user.id)
        await interaction.followup.send(f"Se ha cambiado a un estado de {'SI' if notify else 'NO'} permitir notificaciones de juegos", ephemeral=True)
        
        
    @app_commands.command(name="event", description="Crea un evento de reunion.")
    @app_commands.describe(title="Titulo del evento",
                           date="Fecha del evento. (Formato DD-MM-YYYY)", time="Hora del evento. (Formato HH:MM y de 24 Horas)",
                           users="Lista de solo usuarios, separados por coma (@Usuario1, @Usuario2, @Usuario3)")
    async def event(self, interaction: discord.Interaction, title: str, date: str, time: str, users:str):
        try:
            users_l = [int(user[2:-1]) for user in list(map(lambda x: x.replace(" ", ""), users.split(',')))]
        except Exception as error:
            if isinstance(error, ValueError):
                return await interaction.response.send_message("Asegurate de agregar bien las comas y que solo sean usuarios los que añadas.", ephemeral=True)
            return await interaction.response.send_message("Está todo bien escrito?", ephemeral=True)
        
        for id_user in users_l:
            user = interaction.guild.get_member(id_user)
            if user.bot:
                return await interaction.response.send_message("NO PUEDES AGREGAR BOTS AL EVENTO", ephemeral=True)

        if interaction.user.id not in users_l: 
            users_l.append(interaction.user.id) 
                
        try:
            date = datetime.datetime.strptime(f"{date} {time}", "%d-%m-%Y %H:%M")
        except Exception as e:
            return await interaction.response.send_message("Seguro que la fecha y hora está bien escritas?", ephemeral=True)
            
        if date <= datetime.datetime.now():
            return await interaction.response.send_message("La fecha y hora no pueden ser pasadas")
        create_event(interaction.user.name, title, date, interaction.guild_id, users_l)
        await interaction.response.send_message(f"Evento creado: {title}, para la fecha {date}")

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
            icon_url="https://images.seeklogo.com/logo-png/27/2/github-logo-png_seeklogo-273183.png",
        )
        embed.set_footer(text="Hecho por Salomón RN")
        embed.add_field(name="🔗 Enlace al Código", value="[Ver en GitHub](https://github.com/SalomonRN/DISCORD-BOT)", inline=False)
        await interaction.response.send_message(embed=embed)

    # ToDo Es mejor hacer otra clase para los comandos de logs y así????
    @app_commands.command(name="error", description="Reporta un bug o error que haya ocurrido.")
    @app_commands.describe(description="Descripcion de como sucedió el error. Que comando usaste y que opciones colocaste.", code="Código del error que el bot arrojó")
    async def error(self, interaction: discord.Interaction, description: str, code: str):
        create_log_bug(description, interaction.guild.name, interaction.user.name, code, None)
        return await interaction.response.send_message("Gracias por reportar el bug, lo revisaré en cuanto pueda 😊", ephemeral=True)
    
    @staticmethod
    async def send_log_error(self, server: discord.Guild, message: str):
        # Esto lo traeré de la base de datos, por ahora lo dejo así
        # channel = mongo.get_server(server.id).get("logs_channel")
        channel = 0 
        if not channel:
            await server.owner.create_dm()
            return await server.owner.send("Ey, parece que no tienes el canal de logs configurado, porfa configura el canal de logs con el comando /configure_bot")
        await server.get_channel(channel).send(message)
    
    @app_commands.command(name="configure_bot", description="Configura el bot en el servidor.")
    async def configure_bot(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("No tienes permisos para ejecutar este comando.",
                                                           ephemeral=True, delete_after=4)
        
        # LO HARÉ CON MODALES
        
        await interaction.response.send_message("Configurando el bot en el servidor...", ephemeral=True)
        
        
    # @app_commands.command(name="valoinfo", description="Busca tus estadísticas de valorant 😊")
    # @app_commands.describe(username="Tu Riot ID, incluye el tagline, o sea el #", game="Elige un tipo de juego para buscar tus estadísticas")
    # async def valoinfo(self, interaction: discord.Interaction, username: str, game: Literal["competitive", "all", "unrated"]):
    #     if not self.DEBUG:
    #         return await interaction.response.send_message('Lastimosamente el servidor gratuito donde está hospedado el bot no permite usar ciertas herramientas para usar este comando, y no tengo como para alquilar uno.', ephemeral=True, delete_after=10)
        
    #     await interaction.response.send_message(f"⏳ Buscando información de {username} en {game} esto puede tardar unos segundos o minutos...", ephemeral=True, delete_after=8.0)
        
    #     # await interaction.response.defer() 
            
    #     stats = await search(f"https://valorant.op.gg/profile/{username.replace("#", "-")}?statQueueId={game}")
    #     if isinstance(stats, str):
    #         return await interaction.followup.send("Ups,", stats.lower())
    #     else:
    #         stats_roles = ""
    #         for rol in stats[1]: 
    #             stats_roles += f"""
    #             Rol: {rol.get("rol_name")}
    #             Pick Rate: {rol.get("pick_rate")}
    #             KDA: {rol.get("kda")}
    #             Winrate: {rol.get("winrate")}
    #             """
                            
    #         embed = Embed(title=f"Estadísticas de {username}",
    #                     description=f"""
    #                     Estadísticas de {username} en {game},
    #                     Rango: {stats[0].get("range")}
    #                     KDA: {stats[0].get("kda")}
    #                     % tiro a la cabeza {stats[0].get("head_shot")}
    #                     % tiro al cuerpo {stats[0].get("body_shot")}
    #                     % tiro a las piernas {stats[0].get("legs_shot")}
    #                     Daño por ronda: {stats[0].get("damage_round")}
    #                     Win Rate: {stats[0].get("win_rate")}
                        
    #                     ROLES
    #                     {stats_roles}
    #                     """,
    #                     color=discord.Color.blue())
    #         await interaction.followup.send(embed=embed)
    
    # @app_commands.command(name="create_rol", description="Crea el rol que quieras")
    # @app_commands.describe(name="El nombre del rol que quieres crear")
    # async def create_rol(self, interaction: discord.Interaction, name: str):
    #     if not self.DEBUG:
    #         return await interaction.response.send_message("Este comando no está finalizado y no lo quiero quitar :)", 
    #                                                        ephemeral=True, delete_after=2)
    #     print(interaction.user.resolved_permissions.manage_roles)
    #     await interaction.guild.create_role(name=name)
    #     await interaction.response.send_message("Rol creado")       
    