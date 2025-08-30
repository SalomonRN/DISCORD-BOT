from core.db import DATABASE

async def create_event(querry: dict):
    await DATABASE.get_collection("events").insert_one(querry)

async def get_events() -> list[dict]: 
    return await DATABASE.get_collection("events").find({})
   
async def delete_event(querry):
    await  DATABASE.get_collection("events").delete_one(querry)
