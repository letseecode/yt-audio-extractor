from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI()


class ExtractRequest(BaseModel):
    url: str


@app.post("/extract")
def extract_audio(request: ExtractRequest):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
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