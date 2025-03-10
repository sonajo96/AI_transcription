import os
from dotenv import load_dotenv
import openai

load_dotenv()

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 5))
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    DATABASE_URL = os.getenv("DATABASE_URL")

settings = Settings()