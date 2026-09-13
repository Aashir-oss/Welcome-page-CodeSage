from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uvicorn

app = FastAPI()

# Serve frontend folder
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app_path = os.path.join(os.path.dirname(__file__), "app", "frontend")

# Mount static if exists
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    # Try root index.html first (FINAL login -> app model)
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    # Then frontend/index.html
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    # Then app/frontend/index.html
    if os.path.exists("app/frontend/index.html"):
        return FileResponse("app/frontend/index.html")
    return {"error": "index.html not found"}

# Include your auth routes if you have app/auth etc
try:
    from app.auth.routes import router as auth_router
    app.include_router(auth_router, prefix="/auth")
    print("Auth routes loaded")
except Exception as e:
    print(f"Auth not loaded (ok for Vercel demo): {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
