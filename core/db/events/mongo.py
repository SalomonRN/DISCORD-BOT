from datetime import datetime
from core.db.events import _mongo

async def get_evetns() -> list:
    return await _mongo.get_events()

async def create_event(username: str, title: str, date: datetime, server_id: int, users : list[int]):
    querry = {
        "username": username,
        "event_name": title,
        "date": date,
        "server": server_id,
        "users": users
    }
    await _mongo.create_event(querry)

async def delete_event(Object_id):
    querry = {
        "_id" : Object_id
    }
    return await _mongo.delete_event(querry)
