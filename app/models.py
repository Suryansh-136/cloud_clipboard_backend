from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.config import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationship: One user has many items
    items: Mapped[list["Item"]] = relationship(
        "Item", back_populates="owner", cascade="all, delete-orphan"
    )


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_type = Column(String, nullable=False)  # 'text', 'link', 'image', 'file'
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)  # Text content or notes
    
    # New file metadata columns
    file_path = Column(String, nullable=True)  # Public MEGA URL
    file_type = Column(String, nullable=True)  # MIME type (e.g. image/png)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to User owner
    owner = relationship("User", back_populates="items")
    items = relationship("Item", back_populates="owner")
