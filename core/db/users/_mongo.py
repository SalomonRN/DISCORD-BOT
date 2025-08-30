import pymongo
from core.db import DATABASE

async def create_user(querry: dict):
    return await DATABASE.get_collection("users").insert_one(querry)

async def get_user_by_id(id: int) -> dict:
    return await DATABASE.get_collection("users").find_one({"discord_id": id})

async def update_user_by_id(id: int, update_querry: dict) -> dict:
    return await DATABASE.get_collection("users").find_one_and_update(
        {"discord_id": id}, update_querry, return_document=pymongo.ReturnDocument.AFTER
    )

async def delete_user(id: int):
    return await DATABASE.get_collection("users").find_one_and_delete({"discord_id": id})
