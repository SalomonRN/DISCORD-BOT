from core.db.users import _mongo
from core.db.users.errors import UserNotFound
from discord  import Member

async def user_exist(id: int) -> bool:
    return True if await _mongo.get_user_by_id(id) else False

async def create_user_in_db(user: Member):

    querry = {
        "discord_id": user.id,
        "name": user.name,
        "notify": False,
        "notify_to": [],
        "playlists": {}
    }
    return await _mongo.create_user(querry)

async def get_user(id: int) -> dict:
    res = _mongo.get_user_by_id(id)
    if res.get("error", False):
        return {"error": "Algo salió mal, contacte al administrados para ver que pasó."}
    else:
        return res

async def delete_user_by_id(user_id: int):
    _mongo.delete_user(user_id)

async def create_new_playlist(user_id: int, playlist_name: str):
    if not await user_exist(user_id):
        raise UserNotFound()
    
    update_querry =  {"$set": {f"playlists.{playlist_name}": []}}
    user = await _mongo.update_user_by_id(user_id, update_querry)
    
    return user

async def add_song_to_playlist(user_id: int, playlist_name: str, song_link: str):
    if not await user_exist(user_id):
        raise UserNotFound()
    
    update_querry = {"$push": {f"playlists.{playlist_name}": song_link}}
    user = await _mongo.update_user_by_id(user_id, update_querry)
    
    return user

async def delete_playlist():
    raise NotImplementedError()

async def delete_song_in_playlist():
    raise NotImplementedError()

async def change_active_status_user(id: int) -> str:
    user = _mongo.get_user_by_id(id)
    update_querry = {"$set": {"notify": not user.get("notify")}}
    user = _mongo.update_user_by_id(id, update_querry)
    return user.get("notify")

async def update_user_notify_list(user_id: int, new_user: int, add: bool) -> bool:
    user: dict= _mongo.get_user_by_id(user_id)
    
    if not user:
        raise UserNotFound()
   
    if add and new_user not in user.get("notify_to"):
        user.get("notify_to").append(new_user)
    elif not add and new_user in user.get("notify_to"):
        user.get("notify_to").remove(new_user)
    else:
        return False
    
    # Si no se hace nada, no se actualiza la base de datos
    update_querry = {"$set": {"notify_to": user.get("notify_to")}}
    user = _mongo.update_user_by_id(user_id, update_querry)
