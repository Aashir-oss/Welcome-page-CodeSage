# run.py
"""
CodeSage AI – Auth backend with real credential verification.
- /auth/register  → create user (bcrypt hashed)
- /auth/login     → verify user, return JWT
- /auth/me        → validate token (used by frontend auto-login)
Serves index.html at "/".
"""

import os
import re
import json
import threading
import bcrypt
import uvicorn
from datetime import datetime, timezone, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, field_validator
from jose import jwt, JWTError

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production-codesage-ai")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "users.json"
INDEX_FILE = BASE_DIR / "index.html"

# Thread lock for safe read-modify-write on users.json
_users_lock = threading.Lock()

app = FastAPI(title="CodeSage AI Auth")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ------------------------------------------------------------------
# USERS STORE  (JSON file with atomic writes + lock)
# ------------------------------------------------------------------
def load_users() -> dict:
    if not USERS_FILE.exists():
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users: dict) -> None:
    """Atomic write to avoid corrupting users.json on crash."""
    tmp = USERS_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    tmp.replace(USERS_FILE)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt(rounds=12)
    ).decode("utf-8")

def verify_password(password: str, stored_hash: str) -> bool:
    """
    Supports BOTH:
      - bcrypt hashes  (start with $2a$/$2b$/$2y$)
      - legacy plaintext (old users.json entries)
    """
    if not stored_hash:
        return False
    if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), stored_hash.encode("utf-8")
            )
        except ValueError:
            return False
    # legacy plaintext comparison
    return password == stored_hash

def is_bcrypt(stored: str) -> bool:
    return bool(stored) and stored.startswith(("$2a$", "$2b$", "$2y$"))

# ------------------------------------------------------------------
# JWT
# ------------------------------------------------------------------
def create_token(username: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "exp": now + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
        "iat": now,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def current_user(token: str = Depends(oauth2_scheme)) -> str:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = data.get("sub")
        if not username:
            raise cred_exc
    except JWTError:
        raise cred_exc

    users = load_users()
    if username not in users:
        raise cred_exc
    return username

# ------------------------------------------------------------------
# MODELS
# ------------------------------------------------------------------
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")

class RegisterBody(BaseModel):
    username: str
    password: str
    email: EmailStr | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not USERNAME_RE.fullmatch(v):
            raise ValueError(
                "Username must be 3-32 chars: letters, digits, _ . -"
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

# ------------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------------
@app.post("/auth/register")
async def register(body: RegisterBody):
    username = body.username
    password = body.password
    email = (str(body.email) if body.email else "").strip()

    with _users_lock:
        users = load_users()
        if username in users:
            raise HTTPException(400, "Username already exists")

        users[username] = {
            "username": username,
            "email": email,
            "password": hash_password(password),
            "created": datetime.now(timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            ),
        }
        save_users(users)

    # Auto-login: return a token right after signup
    token = create_token(username)
    return {
        "message": "Account created",
        "username": username,
        "access_token": token,
        "token_type": "bearer",
    }


@app.post("/auth/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 form login – matches frontend `application/x-www-form-urlencoded` POST."""
    username = form.username.strip()
    password = form.password

    users = load_users()
    user = users.get(username)

    if not user:
        # Do NOT leak whether username exists
        raise HTTPException(401, "Invalid username or password")

    stored = user.get("password", "")
    if not verify_password(password, stored):
        raise HTTPException(401, "Invalid username or password")

    # Upgrade legacy plaintext hash to bcrypt on successful login
    if not is_bcrypt(stored):
        with _users_lock:
            users = load_users()
            if username in users:
                users[username]["password"] = hash_password(password)
                save_users(users)

    token = create_token(username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": username,
    }


@app.get("/auth/me")
async def me(username: str = Depends(current_user)):
    users = load_users()
    u = users.get(username, {})
    return {
        "username": username,
        "email": u.get("email", ""),
        "created": u.get("created", ""),
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": "https://aashir-oss-codesage-ai-app-nerb3i.streamlit.app/",
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    if INDEX_FILE.exists():
        return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))
    return HTMLResponse(
        "<h1>CodeSage AI – backend running. "
        "Put index.html next to run.py.</h1>"
    )


if __name__ == "__main__":
    print("CodeSage AI backend → http://127.0.0.1:8000")
    print(f"Users file: {USERS_FILE}")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
