from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.database import db
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
import os

router = APIRouter(prefix="/auth", tags=["auth"])
users_collection = db["users"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class UserCreate(BaseModel):
    username: str
    password: str

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
def register(user: UserCreate):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="User already exists")
    users_collection.insert_one({
        "username": user.username,
        "password": get_password_hash(user.password)
    })
    return {"msg": "User registered"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}