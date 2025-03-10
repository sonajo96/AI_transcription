from pydantic import BaseModel,Field,validator

class UserCreate(BaseModel):
    mobile_phone:  str = Field(..., min_length=10, max_length=10)
    name: str
    password: str

    @validator('mobile_phone')
    def validate_mobile_phone(cls, v):
        if not v.isdigit():
            raise ValueError('Mobile phone must contain only digits')
        if len(v) != 10:
            raise ValueError('Please enter a 10-digit number')
        return v

class UserLogin(BaseModel):
    mobile_phone: str=Field(..., min_length=10, max_length=10)
    password: str

    @validator('mobile_phone')
    def validate_mobile_phone(cls, v):
        if not v.isdigit():
            raise ValueError('Mobile phone must contain only digits')
        if len(v) != 10:
            raise ValueError('Please enter a 10-digit number')
        return v

class VideoCreate(BaseModel):
    url: str

class ChatRequest(BaseModel):
    question: str
    