from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
import os

from app.config import get_db
from app.routes import auth, items

app = FastAPI(
    title="Cloud Clipboard",
    description="Backend API for personal cross-device workspace",
    version="0.1.0",
)

# Register API endpoints
app.include_router(auth.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def read_root():
    """Serve the main frontend UI."""
    return FileResponse("frontend/index.html")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        return {"database_status": "connected", "result": result[0]}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection failed: {str(e)}"
        )