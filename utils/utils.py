import aiohttp
from gtts import gTTS
import sys
import discord
async def get_advice() -> str:
    from googletrans import Translator
    import requests

    translator = Translator()

    text = requests.get("https://api.adviceslip.com/advice").json()["slip"]
    translate = await translator.translate(text["advice"], src="en", dest="es")
    return translate.text

def create_audio(message: str) -> str:
    tts = gTTS(message, lang='es')
    filename = "audio.mp3"
    tts.save(filename)
    return filename

def load_libopus() -> bool:
    if sys.platform.startswith('linux'):
        discord.opus.load_opus("./bin/linux/libopus.dll")
        return discord.opus.is_loaded()
        
    elif sys.platform.startswith('win'):
        discord.opus.load_opus("./bin/win/libopus.dll")
        return discord.opus.is_loaded()

if __name__ == "__main__":
    create_audio("Hola, este es un mensaje de prueba.")