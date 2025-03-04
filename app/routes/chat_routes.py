from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.video import Video
from app.models.chat import ChatHistory
from app.services.ai_chat import generate_answer
from app.schemas import ChatRequest
from app.auth import get_current_user

router = APIRouter()

@router.post("/ask/")
def ask_question(
    request: ChatRequest, 
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    # Fetch the video and verify it belongs to the authenticated user
    video = db.query(Video).filter(
        Video.video_url == request.url,
        Video.user_id == current_user_id
    ).first()
    
    if not video:
        raise HTTPException(
            status_code=404, 
            detail="Video not found or you don't have access to it"
        )
   
    answer = generate_answer(request.question, video.transcription)
   
    chat_entry = ChatHistory(
        video_id=video.id, 
        user_id=current_user_id, 
        question=request.question, 
        answer=answer
    )
    
    print(f"Creating chat entry: {chat_entry}")
    
    try:
        db.add(chat_entry)
        db.commit()
        print("Chat entry committed successfully")
    except Exception as e:
        db.rollback()
        print(f"Error committing to database: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
   
    return {"question": request.question, "answer": answer}

@router.get("/chathistory/")
def get_chat_history(
    db: Session = Depends(get_db), 
    user_id: int = Depends(get_current_user)
):
    # Fetch only videos belonging to the authenticated user
    user_videos = db.query(Video).filter(Video.user_id == user_id).all()
    if not user_videos:
        raise HTTPException(status_code=404, detail="No videos found for this user")

    video_ids = [video.id for video in user_videos]
    # Fetch chat history only for the user's videos
    history = db.query(ChatHistory).filter(
        ChatHistory.video_id.in_(video_ids),
        ChatHistory.user_id == user_id
    ).all()

    return [{"question": h.question, "answer": h.answer} for h in history]