import aiohttp
from gtts import gTTS
import sys
import discord
from pathlib import Path

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
        discord.opus.load_opus(Path(__file__).parent.parent.joinpath("./bin/linux/libopus.so"))
        return discord.opus.is_loaded()
        
    elif sys.platform.startswith('win'):
        discord.opus.load_opus(Path(__file__).parent.parent.joinpath("./bin/win/libopus.dll"))
        return discord.opus.is_loaded()
def ffmpeg_path():
    if sys.platform.startswith('linux'):
        return "./bin/linux/ffmpeg"
        
    elif sys.platform.startswith('win'):
        return "./bin/win/ffmpeg.exe"

if __name__ == "__main__":
    pass
