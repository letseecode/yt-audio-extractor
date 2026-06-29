import os
import glob
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
    temp_dir = tempfile.gettempdir()
    output_template = os.path.join(temp_dir, "audio.%(ext)s")

    for f in glob.glob(os.path.join(temp_dir, "audio.*")):
        os.remove(f)

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "cookiefile": "cookies.txt",
        "remote_components": ["ejs:github"],
        "outtmpl": output_template,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)
            title = info.get("title", "Unknown title")

        matches = glob.glob(os.path.join(temp_dir, "audio.*"))
        if not matches:
            raise HTTPException(status_code=500, detail="Downloaded file not found on disk.")

        actual_path = matches[0]

        return FileResponse(
            actual_path,
            media_type="audio/mp4",
            filename="audio" + os.path.splitext(actual_path)[1],
            headers={"X-Video-Title": title},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def health_check():
    return {"status": "ok"}