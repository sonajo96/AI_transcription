
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth import create_access_token
from app.utils.security import get_password_hash, verify_password
from app.schemas import UserCreate, UserLogin
from fastapi.security import OAuth2PasswordBearer
from app.auth import invalidate_token, get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/signup/")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.mobile_phone == user.mobile_phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = get_password_hash(user.password)
    new_user = User(mobile_phone=user.mobile_phone, name=user.name, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}

@router.post("/login/")
def login(user: UserLogin = Body(...), db: Session = Depends(get_db)):
    user_record = db.query(User).filter(User.mobile_phone == user.mobile_phone).first()
    if not user_record or not verify_password(user.password, user_record.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user_record.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout/")
def logout(token: str = Depends(oauth2_scheme)):
    # Invalidate the token by adding it to the blacklist
    invalidate_token(token)
    return {"message": "Successfully logged out"}