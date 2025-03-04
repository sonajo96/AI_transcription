import os
import yt_dlp
import whisper
from fastapi import HTTPException
from app.config import settings
from app.models.video import Video
from app.models.user import User
from app.database import get_db

model = whisper.load_model("base")

TMP_FOLDER = os.path.abspath("tmp")
os.makedirs(TMP_FOLDER, exist_ok=True)

def extract_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': ['-ar', '16000'],
        'noplaylist': True,
        'outtmpl': os.path.join(TMP_FOLDER, "%(id)s.%(ext)s"),
        'quiet': False,
        'retries': 3,
        'geo_bypass': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_id = info_dict['id']
            original_ext = info_dict['ext']
            downloaded_filename = os.path.join(TMP_FOLDER, f"{video_id}.{original_ext}")
            audio_filename = os.path.join(TMP_FOLDER, f"{video_id}.mp3")

            if not os.path.exists(audio_filename) or os.path.getsize(audio_filename) < 1000:
                raise HTTPException(status_code=400, detail="Extracted audio is invalid or empty")

        return audio_filename
   
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract audio: {e}")

def transcribe_audio(audio_filename):
    try:
        result = model.transcribe(audio_filename)
        return result['text']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transcribe audio: {e}")

def process_video(url, user_id, db):
    try:
        audio_file = extract_audio(url)
        transcription = transcribe_audio(audio_file)
        print("Transcription:")
        print(transcription)
        db_video = Video(video_url=url, transcription=transcription, user_id=user_id)
        db.add(db_video)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {e}")