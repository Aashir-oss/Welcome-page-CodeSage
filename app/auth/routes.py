from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.database import db
from datetime import datetime
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/code", tags=["Code RAG"])
codes_collection = db["codes"]

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class ChatQuery(BaseModel):
    question: str

@router.post("/upload")
def upload_code(file: UploadFile = File(...), username: str = Depends(get_current_user)):
    content = file.file.read().decode("utf-8", errors="ignore")[:10000]
    codes_collection.insert_one({
        "username": username,
        "filename": file.filename,
        "content": content,
        "uploaded_at": datetime.utcnow()
    })
    return {"msg": f"{file.filename} saved on MongoDB Cloud", "owner": username}

@router.get("/my-codes")
def my_codes(username: str = Depends(get_current_user)):
    codes = list(codes_collection.find({"username": username}, {"_id": 0, "content": 0}))
    return {"count": len(codes), "codes": codes}

@router.post("/chat")
def chat(query: ChatQuery, username: str = Depends(get_current_user)):
    all_codes = list(codes_collection.find({"username": username}))
    if not all_codes:
        return {"answer": "Pehle koi code upload karo!"}
    relevant = [c["filename"] for c in all_codes if query.question.lower() in c["content"].lower()]
    if relevant:
        return {"answer": f"Iska jawab in files me mil sakta hai: {', '.join(relevant)}"}
    else:
        return {"answer": f"{len(all_codes)} files hain, par direct match nahi mila."}