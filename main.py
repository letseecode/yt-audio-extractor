import os
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
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
    output_path = os.path.join(tempfile.gettempdir(), "audio.m4a")

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "cookiefile": "cookies.txt",
        "remote_components": ["ejs:github"],
        "outtmpl": output_path,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)
            title = info.get("title", "Unknown title")

        # yt-dlp may adjust the extension depending on the actual format downloaded
        actual_path = ydl.prepare_filename(info)

        return FileResponse(
            actual_path,
            media_type="audio/m4a",
            filename="audio.m4a",
            headers={"X-Video-Title": title},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def health_check():
    return {"status": "ok"}