import discord
import mongo

# FUNCTIONS
def create_server_in_db(guild: discord.Guild):
    querry = {
        "name": guild.name,
        "id": guild.id,
    }
    mongo.create_server(querry)

def create_user_in_db(user: discord.Member):
    
    querry = {
        "discord_id": user.id,
        "name": user.name,
        "notify": False,
        "active": True,
        "server_id": user.guild.id
    }
    mongo.create_user(querry)

def user_exist(id: int) -> bool:
    return True if mongo.get_user_by_id(id) else False

def get_user(id: int) -> dict:
    res =  mongo.get_user_by_id(id)
    if res.get('error', False):
        return {'error': 'Algo salió mal, contacte al administrados para ver que pasó.'}
    else:
        return res

def change_active_status_user(id: int) -> str:
    user = mongo.get_user_by_id(id)
    update_querry = {"$set": {"notify": not user.get("notify")}}
    user =  mongo.update_user_by_id(id, update_querry)
    return user.get('notify')

def get_server(id: int) -> dict:
    return mongo.get_server(id)

def server_exist(id: int) -> bool:
    return True if mongo.get_server(id) else False

def delete_server_data(id: int):
    mongo.delete_server(id)
    querry = {"server_id": id}
    mongo.delete_server_data(querry)

def change_active_status(id: int):
    server = mongo.get_server(id)
    querry = {"$set": {"active": not server.get("active")}}
    mongo.update_server(id, querry)

def update_server_info(server: discord.Guild):
    querry = {"$set": {"name": server.name}}
    mongo.update_server(server.id, querry)    
    

def update_list(id, server_id: int, remove = False): 
    user = mongo.get_user_by_id(id)
    new: list = user.get('servers_id')
    if remove: new.remove(server_id)
    else: new.append(server_id)

    querry = {'$set': {"servers_id": new}}
    mongo.update_user_by_id(id, querry)
    
def get_advice() -> str:
    from googletrans import Translator
    import requests
    translator = Translator()

    text = requests.get("https://api.adviceslip.com/advice").json()['slip']
    translate = translator.translate(text['advice'], src='en', dest='es')
    return translate.text

