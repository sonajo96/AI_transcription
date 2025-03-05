from pydantic import BaseModel

class UserCreate(BaseModel):
    mobile_phone: str
    name: str
    password: str

class UserLogin(BaseModel):
    mobile_phone: str
    password: str

class VideoCreate(BaseModel):
    url: str

class ChatRequest(BaseModel):
    question: str
    