from datetime import datetime, timedelta
from discord.ext import tasks, commands
from discord import Embed, Colour, Member
from utils.mongo_utils import get_evetns, delete_event

class EventTask(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.index = 0
        self.event.start()
        
    def cog_unload(self):
        self.event.cancel()
   
    @tasks.loop(seconds=60.0)
    async def event(self):
        # MEJOR USAR FILTRO, ASI NO RECORREMOS TODOS LOS EVENTOS
        events: list[dict] = await get_evetns()

        for event in events:
            date_event = event.get('date')
            server = self.bot.get_guild(int(event.get('server')))
            users = [server.get_member(id_) for id_ in event.get('users')]
            
    # LA HORA ACTUAL ES MENOR A LA DEL EVENTO, Y ESTA EN UN RANGO DE 5 MINUTOS MENOS
            if datetime.now() < date_event and datetime.now() >= (date_event - timedelta(minutes=5)):
                msg = f"Ey!! El evento {event.get("event_name", "de hoy")} ya va a iniciar, no te olvides te ingresar al voice en {server.name}, o si no sos puto!"
                for user in users:
                    await self.send_message(user, msg)
                continue
            
    # LA HORA ACTUAL ES MAYOR A LA DEL EVENTO, Y ESTA EN UN RANGO DE 5 MINUTOS MAS
            if datetime.now() > date_event and datetime.now() < (date_event + timedelta(minutes=5)):
        # ASUMIMOS QUE NINGUN USUARIO ESTA EN LOS VOICE
                users_ausentes = users.copy()
        # RECORREMOS CADA VOICE CHANNEL PARA SABER QUE USUARIOS HAY
                for channel in server.voice_channels:
            # RECORREMOS CADA INVITADO AL EVENTO
                    for user in users:
                # SI EL USUARIO ESTÁ EN UN VOICE SIGNIFICA QUE YA ESTÁ EN EL EVENTO
                        if user in channel.members:
                    # POR LO TANTO LO ELIMINAMOS DE USUARIOS AUSENTES
                            users_ausentes.remove(user)

                for user in users_ausentes:
                    msg = f"Ey el evento {event.get("event_name", "de hoy")} en {server.name}, hecho por {event.get("username", "tu migo")},  inició y te están esperando. Unete o culo si no."
                    await self.send_message(user, msg)
                continue

    # SI EL EVENTO ES MAYOR A LA HORA DEL EVENTO MAS CINCO, ELIMINAR DICHO EVENTO
            if date_event + timedelta(5) > datetime.now():
                delete_event(event.get('_id'))
                continue

    async def send_message(self, user: Member, message: str):
        try:
            await user.create_dm()
            await user.dm_channel.send(message, tts=True)    
        except Exception as error:
            print("ERROE MESSAGE")
            print(error)
