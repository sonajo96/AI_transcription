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
    # Fetch the latest video transcription for the user
    latest_video = db.query(Video).filter(Video.user_id == current_user_id).order_by(Video.id.desc()).first()
    
    # Use the transcription as context (if available)
    context = latest_video.transcription if latest_video else ""

    # Generate answer using the question and context
    answer = generate_answer(request.question, context)
    
    # Create a chat entry to store in the database
    chat_entry = ChatHistory(
        user_id=current_user_id,
        question=request.question,
        answer=answer
    )
    
    try:
        db.add(chat_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save chat entry: {str(e)}")
    
    return {"question": request.question, "answer": answer}

@router.get("/chathistory/")
def get_chat_history(
    db: Session = Depends(get_db), 
    user_id: int = Depends(get_current_user)
):
    # Fetch chat history only for the authenticated user
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id
    ).all()

    return [{"question": h.question, "answer": h.answer} for h in history]