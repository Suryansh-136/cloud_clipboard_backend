from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_db
from app.routes import auth, items

app = FastAPI(
    title="Personal Digital Bridge API",
    description="Backend API for personal cross-device workspace",
    version="0.1.0",
)

# Register endpoints
app.include_router(auth.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to Personal Digital Bridge API"}


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