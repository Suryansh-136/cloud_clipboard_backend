from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
import app.models
from app.cleanup import delete_expired_items
from app.config import Base, engine, get_db
from app.routes import auth, items

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Setup Background Scheduler
scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs cleanup job every 30 minutes
    scheduler.add_job(delete_expired_items, "interval", minutes=30)
    scheduler.start()
    print("[Scheduler] Background cleanup task started.")
    yield
    scheduler.shutdown()
    print("[Scheduler] Background cleanup task stopped.")


# Single FastAPI instance with lifespan and metadata
app = FastAPI(
    title="Cloud Clipboard",
    description="Backend API for personal cross-device workspace",
    version="0.1.0",
    lifespan=lifespan,
)

origins = [
    #"http://localhost:5173",
    "https://cloud-clipboard-frontend.vercel.app/login"  # Apne exact Vercel frontend URL se replace karo


]


# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers with /api/v1 prefix
app.include_router(auth.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")


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


# Serve frontend static files at root
# Note: html=True automatically serves frontend/index.html when hitting '/'
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")