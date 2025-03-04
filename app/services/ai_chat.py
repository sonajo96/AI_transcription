import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash-latest")

def generate_answer(question, context):
    return gemini_model.generate_content(f"Question: {question}\nContext: {context}\nAnswer:").text