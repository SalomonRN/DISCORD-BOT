import aiohttp
from gtts import gTTS

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

if __name__ == "__main__":
    create_audio("Hola, este es un mensaje de prueba.")