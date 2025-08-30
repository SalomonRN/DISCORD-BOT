from datetime import datetime
from core.db.ideas import _mongo

async def create_idea(description: str, server: str, user: str):
    querry = {
        "created_at": datetime.now(),
        "description": description,
        "server": server,
        "user": user
    }
    await _mongo.create_idea(querry)