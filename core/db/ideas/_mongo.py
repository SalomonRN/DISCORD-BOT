from core.db import DATABASE

async def create_idea(querry: dict):
    await DATABASE.get_collection("ideas").insert_one(querry)
