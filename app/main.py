from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from app.auth.routes import router as auth_router
from app.codes.routes import router as codes_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(codes_router)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_FILE = BASE_DIR / "frontend" / "index.html"

@app.get("/")
def home():
    return FileResponse(str(FRONTEND_FILE))

@app.get("/health")
def health():
    return {"ok": True}