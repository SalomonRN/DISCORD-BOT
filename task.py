from discord.ext import tasks, commands
from discord import Embed, Colour


class Task(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.index = 0
        self.printer.start()
        self.client = client
        self.guild = client.get_guild(795858207171412018)

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=5.0)
    async def printer(self):
        channel = self.guild.get_channel(1227407066868613240)
        invites = await self.guild.invites()
        embeds = []
        for i in invites:
            embed = Embed(
                color=Colour.blue(),
                title="Invitacion eliminada",
                description=f"Se ha eliminado la invitacion\
                Datos:\
                Creada por {i.inviter}\
                Creada a las {i.created_at}\
                Se usó un total de {i.uses} veces.",
            )
            embed.set_author(
                name="KimeBot",
                icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS8paEvGt3sACXnfgr_NPr010dg0uFjtXZBbQ&s",
            )
            embed.set_footer(text="Hecho por Salomón")
            embeds.append(embed)
            await i.delete()
            await channel.send(embeds=embeds)
