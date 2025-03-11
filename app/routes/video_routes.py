from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.video import Video
from app.schemas import YouTubeTranscriptionRequest
from app.services.video_services import transcribe_audio_file
from app.auth import get_current_user

router = APIRouter()
@router.post("/transcribe/youtube/")
async def transcribe_youtube_video(
    request: YouTubeTranscriptionRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)  # Fetch the authenticated user's ID
):
    transcription = transcribe_audio_file(request.video_id)
    print(f"Received video ID: {request.video_id}")
    print("Transcription:", transcription)

    # Save the transcription to the database
    video_entry = Video(
        user_id=current_user_id,  # Use the authenticated user's ID
        video_url=f"https://www.youtube.com/watch?v={request.video_id}",
        transcription=transcription
    )
    
    try:
        db.add(video_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save video entry: {str(e)}")

    return {"message": "Transcription saved successfully"}