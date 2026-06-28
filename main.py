import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

cookies_content = os.environ.get("YOUTUBE_COOKIES", "")
if cookies_content:
    with open("cookies.txt", "w") as f:
        f.write(cookies_content)

app = FastAPI()


class ExtractRequest(BaseModel):
    url: str


@app.post("/extract")
def extract_audio(request: ExtractRequest):
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "cookiefile": "cookies.txt",
        "remote_components": ["ejs:github"],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            audio_url = info["url"]
            title = info.get("title", "Unknown title")

        return {
            "audio_url": audio_url,
            "title": title,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def health_check():
    return {"status": "ok"}