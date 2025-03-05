from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.video import Video
from app.services.video_services import transcribe_audio_file
from app.auth import get_current_user

router = APIRouter()

@router.post("/transcribe/audio/")
async def transcribe_audio(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    Endpoint to upload an audio file, transcribe it into text, and optionally save it.
    
    Args:
        audio (UploadFile): The audio file to transcribe.
        db (Session): Database session dependency.
        current_user_id (int): ID of the authenticated user.
    
    Returns:
        dict: Contains the transcription text.
    """
    # Transcribe the audio file
    transcription = transcribe_audio_file(audio)

    # Optionally save the transcription with a video entry (assuming a URL or placeholder)
    video = Video(
        user_id=current_user_id,
        video_url=f"audio://{audio.filename}",  # Placeholder; adjust as needed
        transcription=transcription
    )
    
    try:
        db.add(video)
        db.commit()
        db.refresh(video)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save transcription: {str(e)}")

    return {"transcription": transcription, "video_id": video.id}