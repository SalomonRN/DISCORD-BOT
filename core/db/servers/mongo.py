from discord import Guild
from core.db.servers import _mongo


# FUNCTIONS

async def get_server(id: int) -> dict:
    return await _mongo.get_server(id)

async def server_exist(id: int) -> bool:
    return True if await _mongo.get_server(id) else False

async def create_server_in_db(guild: Guild):
    querry = {
        "name": guild.name,
        "id": guild.id,
    }
    await _mongo.create_server(querry)

async def update_server_info(server: Guild):
    querry = {"$set": {"name": server.name}}
    await _mongo.update_server(server.id, querry)

async def change_server_status():
    raise NotImplementedError()

