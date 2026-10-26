import os
import datetime
import asyncio
import discord
from discord import Colour, app_commands
from discord.embeds import Embed
import discord.ext
import discord.ext.commands
from cogs.views import UserCreateView
from core.db.users.mongo import delete_user_by_id
from core.db.ideas.mongo import create_idea
from core.db.events.mongo import create_event
from utils.utils import get_advice, create_audio, load_libopus
import re

class CommandsBot(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot: discord.ext.commands.Bot = bot

    @app_commands.command(name="prefix", description="Te dice que prefijo se usa en el servidor")
    async def prefix(self, interaction: discord.Interaction):
        return await interaction.response.send_message(f"Este servidor usa el prefijo: {self.bot.command_prefix}" ,ephemeral=True)
    
    @app_commands.command(name="ping", description="Responde con un pong")
    async def ping(self, interaction: discord.Interaction):
        embed = Embed(
            color=Colour.blue(),
            title="🏓Pong!",
            description=f"**ms {round(self.bot.latency, 1)}**"
        )
        return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="advice", description="Te da un consejo totalmente random. La traducción es hecha por google translate, y no es exacta.")
    async def advice(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Y el consejo es...", ephemeral=True, delete_after=1.8)
        advice = await get_advice()
        return await interaction.followup.send(advice)     

    @app_commands.command(name="createuser", description="Crea tu usuario en la base de datos.")
    async def create_user(self, interaction: discord.Interaction):
        embed = Embed()
        embed.color = Colour.blue()
        embed.set_author(name="Creacion de usuario en la base de datos", icon_url=self.bot.user.display_avatar.url)
        embed.description = f"Al aceptar, le estás dando permiso a {self.bot.user.mention} para que guarde cierta informacion tuya.\n"
        embed.add_field(name="¿Que informacion se guardará?", value="Si aceptas, se te creará un usuario en la base de datos y guardaré tu username y tu discord id", inline=False)
        embed.add_field(name="¿Que se puede hacer con esta informacion?", value="Realmente no mucho, solo se hace para acceder a estos datos de manera rapida y a futuro poder configurar tu experiencia con el bot.", inline=False)
        embed.set_footer(text="Si quieres eliminar tu informacion de la base de datos usa el comando /deleteuser")
        return await interaction.response.send_message(embed=embed, view=UserCreateView(interaction.user), ephemeral=True)
    
    @app_commands.command(name="deleteuser", description="Elimina tu usuario de la base de datos.")
    async def delete_user(self, interaction: discord.Interaction):
        delete_user_by_id(interaction.user.id)
        await interaction.response.send_message("Tu usuario ha sido eliminado de la base de datos. Si quieres volver a crear tu usuario, usa el comando /createuser", ephemeral=True)
    
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

    @app_commands.command(name="idea", description="Quieres hacer una sugerencia? Aquí puedes hacerlo 😊")
    @app_commands.describe(idea="Escribe tu idea o sugerencia aquí")
    async def idea(self, interaction: discord.Interaction, idea: str):
        create_idea(idea, interaction.guild.name, interaction.user.name)
        await interaction.response.send_message("Tu idea ha sido enviada al desarrollador. Gracias por tu sugerencia!", ephemeral=True, delete_after=3)
    
    @app_commands.command(description="Envía un mensaje al voice que tú quieras sin la necesidad de entrar 😉")
    @app_commands.describe(message="Mensaje que quieres que diga el bot.", voice="Voice al que va a entrar el bot.")
    async def message(self, interaction: discord.Interaction, message: str, voice: discord.VoiceChannel):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Este comando es mas propenso a fallar, si el bot no te responde con un mensaje de exito por favor usa >message")
        if "<@" in message:
            print("⚠️ Mensaje con mención detectado")
            list_users = re.findall(r"<@\d+[0-9]>", message) # Encuentra todas las menciones de usuarios en el mensaje
            
            for user in list_users:
                message = message.replace(user, self.bot.get_user(int(user[2:-1])).name)
               
        file_name = await asyncio.to_thread(create_audio, message)
        if not os.path.exists(file_name):
            return await interaction.followup.send("⚠️ Ocurrió un error al generar el audio. Intenta de nuevo sin emojis o caracteres especiales.", ephemeral=True)
        
        if not load_libopus():
            return await interaction.followup.send("⚠️ Error al cargar la librería Opus. Código: 4", ephemeral=True)

        # Solo desconectamos al final si fuimos nosotros los que conectamos el bot.
        connected_by_us = False

        try:
            # Reutilizamos la conexión existente: desconectar y reconectar provoca que el
            # bot salga y vuelva a entrar al voice, y además el connect() se adelanta al
            # voice state update del gateway (ClientException / timeout).
            bot_vc = interaction.guild.voice_client

            if not bot_vc:
                print("🔌 Conectando al canal de voz...")
                bot_vc = await voice.connect(timeout=30.0, reconnect=True)
                connected_by_us = True
                print("🔌 Conectado al canal de voz!")
            elif bot_vc.channel != voice:
                print("🔁 Moviendo a otro canal...")
                # move_to espera a que el gateway confirme el cambio de canal
                await bot_vc.move_to(voice, timeout=30.0)

            # Detener si está reproduciendo
            if bot_vc.is_playing():
                bot_vc.stop()

            # Reproducir el audio. El callback 'after' corre en otro hilo, así que
            # avisamos al loop de forma thread-safe en vez de hacer polling.
            finished = asyncio.Event()
            loop = self.bot.loop

            def after_playing(error):
                if error:
                    print(f"❌ Error al reproducir: {error}")
                else:
                    print("✅ Reproducción terminada.")
                loop.call_soon_threadsafe(finished.set)

            audio = discord.FFmpegPCMAudio(file_name)
            bot_vc.play(audio, after=after_playing)

            print("🎶 Reproduciendo...")
            await interaction.followup.send(f"✅ Reproduciendo mensaje en **{voice.name}**.")

            # Esperar a que termine
            await finished.wait()

            if connected_by_us and bot_vc.is_connected():
                await bot_vc.disconnect()

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
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
    
    # @app_commands.command(description="Es un secreto 🤫")
    # async def init_users(self, interaction: discord.Interaction):
    #     """ Inicializa los usuarios en la base de datos """
    #     if not interaction.user.resolved_permissions.administrator:
    #         return await interaction.response.send_message('NO tienes permisos para ejecutar este comando', ephemeral=True)
        
    #     members = [member for member in interaction.guild.members if not member.bot]
    #     for user in members:
    #         create_user_in_db(user)
    #     return await interaction.response.send_message('Parece que ya.', ephemeral=True)
    
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
        
    # @app_commands.command(name="change_notify", description="Cambia el estado de las notificaciones cuando juegas")
    # async def change_notify(self, interaction: discord.Interaction):
    #     await interaction.response.send_message("Este comando no está aún bien hecho, así que puede dar errores, tales como no hacer nada o explotar el Sol, tenlo presente.", ephemeral=True, delete_after=5)
    #     if interaction.user.bot: return
        
    #     notify = change_active_status_user(interaction.user.id)
    #     await interaction.followup.send(f"Se ha cambiado a un estado de {'SI' if notify else 'NO'} permitir notificaciones de juegos", ephemeral=True)
    
    # @app_commands.command(description="Muestra qué y quiénes están jugando algo ahora mismo.")
    # async def games(self, interaction: discord.Interaction):

    #     if not interaction.user.guild_permissions.administrator:
    #         return await interaction.response.send_message("No tienes permisos para ejecutar este comando.",
    #                                                        ephemeral=True, delete_after=4)

    #     if not self.DEBUG:
    #         await interaction.response.send_message("Este comando aún está en desarrollo. Puede tener errores impredecibles.",
    #                                                 ephemeral=True, delete_after=5)
    #         await asyncio.sleep(1)

    #     jugadores = [
    #         f"{member.display_name} está jugando {member.activity.name}"
    #         for member in interaction.guild.members
    #         if not member.bot and member.activity and member.activity.type == discord.ActivityType.playing
    #     ]

    #     send = ( interaction.followup.send if interaction.response.is_done() else interaction.response.send_message )

    #     if not jugadores:
    #         return await send("Parece que nadie está jugando algo...", ephemeral=True, delete_after=4)

    #     mensaje = "\n".join(jugadores)
    #     await send(mensaje, ephemeral=True)
