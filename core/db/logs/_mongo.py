from core.db import DATABASE

async def create_log(querry: dict):
    await DATABASE.get_collection("logs").insert_one(querry)
