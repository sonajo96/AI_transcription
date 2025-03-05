from fastapi import FastAPI
from app.routes import auth_routes, video_routes, chat_routes
from app.config import settings
from app.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import warnings


warnings.simplefilter("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

app = FastAPI()

app.mount("/static",StaticFiles(directory="frontend"),name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_routes.router)
app.include_router(video_routes.router)
app.include_router(chat_routes.router)

# Create database tables
Base.metadata.create_all(bind=engine)