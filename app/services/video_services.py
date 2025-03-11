import warnings
warnings.simplefilter("ignore",category=FutureWarning)

from youtube_transcript_api import YouTubeTranscriptApi
from fastapi import HTTPException
from app.utils.logger import logger

def transcribe_audio_file(video_id: str) -> str:
    """
    Fetches the transcript of a YouTube video using the YouTubeTranscriptApi.

    Args:
        video_id (str): The ID of the YouTube video.

    Returns:
        str: The transcribed text.

    Raises:
        HTTPException: If transcript retrieval fails.
    """
    try:
        logger.info(f"Fetching transcript for YouTube video ID: {video_id}")
        
        get_transcribe = YouTubeTranscriptApi.get_transcript(video_id)
        final_transcribe = " ".join(each_transcribe['text'] for each_transcribe in get_transcribe)
        
        logger.info(f"Transcript fetched successfully for video ID: {video_id}")
        return final_transcribe

    except Exception as e:
        logger.error(f"Failed to fetch transcript for video ID {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch transcript: {str(e)}")
