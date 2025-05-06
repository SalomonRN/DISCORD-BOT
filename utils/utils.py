import aiohttp

async def get_advice() -> str:
    from googletrans import Translator
    import requests

    translator = Translator()

    text = requests.get("https://api.adviceslip.com/advice").json()["slip"]
    translate = await translator.translate(text["advice"], src="en", dest="es")
    return translate.text

async def say_message(msg: str) -> str | None:
    tts_url = "https://ttsmp3.com/makemp3_new.php"
    payload = {
        "msg": msg,
        "lang": "Conchita",  # Puedes cambiar por otro idioma o voz si quieres
        "source": "ttsmp3",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(tts_url, data=payload, headers=headers) as resp:
                if resp.status != 200:
                    print("❌ Error al contactar TTSMP3")
                    return None

                json_data = await resp.json()
                mp3_url = json_data.get("URL")
                if not mp3_url:
                    print("❌ No se encontró URL del audio")
                    return None

            # Descargar el archivo MP3
            async with session.get(mp3_url) as audio_resp:
                if audio_resp.status != 200:
                    print("❌ Error al descargar el archivo MP3")
                    return None

                audio_data = await audio_resp.read()

                filename = "voz.mp3"
                with open(filename, "wb") as f:
                    f.write(audio_data)

                return filename

    except Exception as e:
        print(f"❌ Error en say_message: {e}")
        return None