import discord
from . import mongo
from datetime import datetime


# FUNCTIONS
def create_server_in_db(guild: discord.Guild):
    querry = {
        "name": guild.name,
        "id": guild.id,
    }
    mongo.create_server(querry)

def create_user_in_db(user: discord.Member):

    querry = {
        "discord_id": user.id,
        "name": user.name,
        "notify": False,
        "active": True,
        "server_id": user.guild.id,
    }
    mongo.create_user(querry)

def user_exist(id: int) -> bool:
    return True if mongo.get_user_by_id(id) else False

def get_user(id: int) -> dict:
    res = mongo.get_user_by_id(id)
    if res.get("error", False):
        return {"error": "Algo salió mal, contacte al administrados para ver que pasó."}
    else:
        return res

def change_active_status_user(id: int) -> str:
    user = mongo.get_user_by_id(id)
    update_querry = {"$set": {"notify": not user.get("notify")}}
    user = mongo.update_user_by_id(id, update_querry)
    return user.get("notify")

def get_server(id: int) -> dict:
    return mongo.get_server(id)

def server_exist(id: int) -> bool:
    return True if mongo.get_server(id) else False

def delete_server_data(id: int):
    mongo.delete_server(id)
    querry = {"server_id": id}
    mongo.delete_server_data(querry)

def change_active_status(id: int):
    server = mongo.get_server(id)
    querry = {"$set": {"active": not server.get("active")}}
    mongo.update_server(id, querry)

def update_server_info(server: discord.Guild):
    querry = {"$set": {"name": server.name}}
    mongo.update_server(server.id, querry)

def update_list(id, server_id: int, remove=False):
    user = mongo.get_user_by_id(id)
    new: list = user.get("servers_id")
    if remove:
        new.remove(server_id)
    else:
        new.append(server_id)

    querry = {"$set": {"servers_id": new}}
    mongo.update_user_by_id(id, querry)

def create_event(username: str, title: str, date: datetime, server_id: int, users : list[int]):
    querry = {
        "username": username,
        "event_name": title,
        "date": date,
        "server": server_id,
        "users": users
    }
    mongo.create_event(querry)
    
async def get_evetns() -> list:
    return mongo.get_events()

def delete_event(Object_id):
    querry = {
        "_id" : Object_id
    }
    return mongo.delete_event(querry)
