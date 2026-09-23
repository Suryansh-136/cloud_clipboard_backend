from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "cloud_clipboard_db"
    DATABASE_URL: str = ""
    SECRET_KEY: str = ""
    MEGA_EMAIL: str = "suryanshsrivastava136@gmail.com"
    MEGA_PASSWORD: str = "@Whysurya420"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v


settings = Settings()

# Database Setup
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Automatically check & reconnect if DB dropped
    pool_size=10,        # Default connection pool size
    max_overflow=20,     # Max extra connections during traffic spikes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that yields a DB session per request and closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()