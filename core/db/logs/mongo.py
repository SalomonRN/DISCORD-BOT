from datetime import datetime
from core.db.logs import _mongo

async def create_log_bug(description: str, server: str, user: str, code: int, command: str):
    querry = {
        "created_at": datetime.now(),
        "description": description,
        "server": server,
        "user": user,
        "code": code,
        "command": command,
    }
    await _mongo.create_log(querry)