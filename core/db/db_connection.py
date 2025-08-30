import sys
from pymongo import AsyncMongoClient
from pymongo.errors import OperationFailure
import os
from dotenv import load_dotenv

load_dotenv()


# https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/
class ClientMongo(AsyncMongoClient):
    """Singleton para la conexión a MongoDB"""

    _instance = None

    # Singleton Logic
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if hasattr(self, "_initialized"):
            return

        URI = os.getenv("URI_MONGO")
        if not URI:
            sys.exit("URI MONGO NOT FOUND")

        super().__init__(URI, **kwargs)
        self._initialized = True

    async def ping_db(self):
        try:
            await self.admin.command("ping")
            print("Conexión exitosa")
        except OperationFailure:
            sys.exit("Conexión no establecida")


client = ClientMongo()
