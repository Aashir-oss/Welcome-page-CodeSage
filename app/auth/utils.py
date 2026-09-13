from passlib.context import CryptContext
from jose import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
def hash_password(password: str):
    return pwd_context.hash(password)
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)
def create_access_token(data: dict, expires_delta: int = 60):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None
