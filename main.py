from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import text
from contextlib import asynccontextmanager
from app.config import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
import os

from app.config import get_db
from app.routes import auth, items
from app.cleanup import delete_expired_items

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Setup Background Scheduler
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Har 30 min mein background cleanup chalega
    scheduler.add_job(delete_expired_items, 'interval', minutes=30)
    scheduler.start()
    print("[Scheduler] Background cleanup task has been started.")
    yield
    scheduler.shutdown()
    print("[Scheduler] Background cleanup task has been stopped.")

app = FastAPI(lifespan=lifespan)

# Enable CORS for browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])


app = FastAPI(
    title="Cloud Clipboard",
    description="Backend API for personal cross-device workspace",
    version="0.1.0",
)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])

# Serve frontend static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

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