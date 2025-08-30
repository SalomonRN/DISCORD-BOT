import pymongo
from core.db import DATABASE


async def create_server(querry: dict):
    await DATABASE.get_collection("servers").insert_one(querry)

async def get_server(id: int) -> dict:
    return await DATABASE.get_collection("servers").find_one({"id": id})

async def update_server(id: int, querry: dict):
    await DATABASE.get_collection("servers").find_one_and_update(
        {"id": id},
        querry,
        return_document=pymongo.ReturnDocument.AFTER,
    )

async def delete_server(id: int):
    return await DATABASE.get_collection("servers").find_one_and_delete({"id": id})
