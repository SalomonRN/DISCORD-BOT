import pymongo
import pymongo.database
import pymongo.errors
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import sys
from os import getenv
from dotenv import load_dotenv
load_dotenv()

URI = getenv("URI_MONGO")
CLIENT = None
DATABASE = None


def init_connection():
    global CLIENT, DATABASE
    try:
        if not URI:
            print("NO SE ENCONTRÓ LA URI DE MONGO")
            sys.exit()
        CLIENT = MongoClient(URI, server_api=ServerApi("1"))
        CLIENT.admin.command("ping")
        DATABASE = CLIENT.get_database("discord")
    except Exception as e:
        sys.exit()


def get_all(database, collection):
    database = CLIENT.get_database(database)
    collection = database.get_collection(collection)
    cursor = collection.find({})
    for element in cursor:
        print(element)

def create_user(querry: dict):
    return DATABASE.get_collection("users").insert_one(querry)

def get_user_by_id(id: int) -> dict:
    return DATABASE.get_collection("users").find_one({"discord_id": id})

def update_user_by_id(id: int, update_querry: dict) -> dict:
    return DATABASE.get_collection("users").find_one_and_update(
        {"discord_id": id}, update_querry, return_document=pymongo.ReturnDocument.AFTER
    )

def delete_user(id: int):
    return DATABASE.get_collection("users").find_one_and_delete({"discord_id": id})

# SERVER
def create_server(querry: dict):
    DATABASE.get_collection("servers").insert_one(querry)

def get_server(id: int) -> dict:
    return DATABASE.get_collection("servers").find_one({"id": id})

def update_server(id: int, querry: dict):
    DATABASE.get_collection("servers").find_one_and_update(
        {"id": id},
        querry,
        return_document=pymongo.ReturnDocument.AFTER,
    )

def delete_server(id: int):
    return DATABASE.get_collection("servers").find_one_and_delete({"id": id})

def delete_server_data(querry: dict):
    DATABASE.get_collection("users").delete_many(querry)

def create_event(querry: dict):
    DATABASE.get_collection("events").insert_one(querry)

def get_events() -> list[dict]: 
    return DATABASE.get_collection("events").find({})
   
def delete_event(querry):
    DATABASE.get_collection("events").delete_one(querry)

def create_log(querry: dict):
    DATABASE.get_collection("logs").insert_one(querry)

def create_idea(querry: dict):
    DATABASE.get_collection("ideas").insert_one(querry)

if __name__ == "__main__":
    init_connection()
    # DATABASE.get_collection("users").create_index("discord_id" , unique = True)
    from datetime import datetime, timedelta
    # create_event({"username": "salo1", "event_name": "EPA juegos?", "date": datetime(2025, 4, 27, 5, 15), "users": [1,2,3,4,5]})
    CLIENT.close()

