from fastapi import HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import settings
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User

# Token blacklist (use Redis or a database in production)
token_blacklist = set()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)) -> int:
    # Check if the token is blacklisted
    if token in token_blacklist:
        raise HTTPException(status_code=401, detail="Token has been invalidated (logged out)")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token: 'sub' missing")
        return int(user_id)
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

def invalidate_token(token: str):
    """Add a token to the blacklist."""
    token_blacklist.add(token)