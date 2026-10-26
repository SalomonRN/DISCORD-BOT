import os
import re
import asyncio
import discord
import discord.ext
import discord.ext.commands
from discord.ext import commands
from utils.utils import create_audio, load_libopus


class SpeakCog(discord.ext.commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot: discord.ext.commands.Bot = bot
       
    @commands.command(name="say", aliases=["msg", "message"])
    async def say(self, ctx: discord.ext.commands.Context):
        if len(ctx.message.content.split(" ")) == 1:
            embed = discord.Embed(colour=0x043548)
            embed.title ="📢 Cómo usar el comando message"
            embed.description= f"¿Quieres que el bot hable por ti en un canal de voz sin unirte ¡Este comando es para ti!\n🔧 Recuerda que el prefijo por defecto es {self.bot.command_prefix}, aunque puede variar según el servidor.\n\n🔸 Enviar un mensaje a otro usuario en un canal de voz:\n** sb>say @usuario Tu mensaje **\n  ➡️ El mensaje será enviado al canal de voz donde se encuentre el usuario mencionado.\n  ⚠️ Asegúrate de que el usuario esté conectado a un canal de voz en el mismo servidor.\n\n🔸 Enviar un mensaje en tu canal de voz actual:\n*** sb>say Tu mensaje ***\n  ➡️ El bot dirá tu mensaje en el canal de voz en el que te encuentres actualmente.\n  ⚠️ Debes estar conectado a un canal de voz para usar esta opción. \n\n🔸 Este comando tiene los siguientes alias: *say* *msg* *message*"
            return await ctx.send(embed=embed, ephemeral=True)
        try:
            vc = None
            flag = False
            
            if not load_libopus():
                # Log de error si no se pudo cargar la librería Opus
                print("Error al cargar la librería Opus. Asegúrate de tenerla instalada.")
                return await ctx.send("⚠️ Error con Opus. Código: 4", ephemeral=True)
            
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
            
            list_users = re.findall(r"<@\d+[0-9]>", ctx.message.content)

            for user in list_users:
                ctx.message.content = ctx.message.content.replace(user, self.bot.get_user(int(user[2:-1])).name)

            if flag:
                message = ctx.message.content.split(" ", 2)[2]
            else:
                message = ctx.message.content.split(" ", 1)[1]

            # gTTS es bloqueante (hace una petición HTTP). Se ejecuta en otro hilo y ANTES de
            # conectar: si bloquea el event loop con el bot ya conectado, el websocket de voz
            # no puede responder, la conexión se cae y play() lanza "Not connected to voice."
            file_name = await asyncio.to_thread(create_audio, message)
            if not os.path.exists(file_name):
                return await ctx.send("No pude crear el audio, revisa el mensaje que enviaste.", ephemeral=True)

            bot_vc = ctx.voice_client

            if not bot_vc:
                bot_vc = await vc.connect()

            elif bot_vc.channel != vc:
                await bot_vc.move_to(vc)

            if bot_vc.is_playing():
                bot_vc.stop()

            bot_vc.play(discord.FFmpegPCMAudio(file_name))
        except Exception as e:
            print(f"Error al conectar al canal de voz: {e}")
            return await ctx.send("Algo salió mal...", ephemeral=True)
