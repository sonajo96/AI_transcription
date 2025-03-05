import warnings
warnings.simplefilter("ignore",category=FutureWarning)

import os
import whisper
from fastapi import UploadFile, HTTPException
from app.utils.logger import logger

model = whisper.load_model("base")

TMP_FOLDER = "tmp"
os.makedirs(TMP_FOLDER, exist_ok=True)

def transcribe_audio_file(audio_file: UploadFile) -> str:
    """
    Transcribes an uploaded audio file into text.
    
    Args:
        audio_file (UploadFile): The audio file uploaded by the user.
    
    Returns:
        str: The transcribed text.
    
    Raises:
        HTTPException: If transcription fails.
    """
    temp_path = os.path.join(TMP_FOLDER, audio_file.filename)
    
    try:

        # Log start of transcription
        logger.info(f"Starting transcription for file: {audio_file.filename}")

        # Save the uploaded file temporarily
        with open(temp_path, "wb") as f:
            f.write(audio_file.file.read())

        # Ensure the file is closed before transcription
        audio_file.file.close()

        # Transcribe the audio file
        result = model.transcribe(temp_path)
        transcription_text = result["text"]

         # Log successful transcription
        logger.info(f"Transcription completed for file: {audio_file.filename}")
        logger.info(f"Transcription: {transcription_text}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transcribe audio file: {str(e)}")
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except PermissionError:
                pass  # Ignore if file is still in use

    return transcription_text