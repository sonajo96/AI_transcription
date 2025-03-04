from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.video import Video
from app.models.user import User
from app.services.video_services import process_video
from app.schemas import VideoCreate
from app.auth import get_current_user

router = APIRouter()

@router.post("/transcribe/")
def transcribe_video(video: VideoCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    background_tasks.add_task(process_video, video.url, user_id, db)
    return {"status": "processing"}

@router.get("/videos/{user_id}")
def get_videos(user_id: int, db: Session = Depends(get_db)):
    videos = db.query(Video).filter(Video.user_id == user_id).all()
    if not videos:
        raise HTTPException(status_code=404, detail="No videos found for this user")
    return [{"video_url": v.video_url, "transcription": v.transcription} for v in videos]
