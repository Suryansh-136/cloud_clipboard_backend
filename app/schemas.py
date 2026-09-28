from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
import secrets

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None


# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, description="Password must be at least 6 characters")


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool = True
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseModel):
    id: int 
    email: str
    share_key: Optional[str]=None

    model_config = ConfigDict(from_attributes=True)

# --- Item Schemas ---
class ItemBase(BaseModel):
    content_type: str  # 'text', 'link', 'file', 'image'
    text_payload: Optional[str] = None
    file_path: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int
    user_id: int
    created_at: datetime


class ItemOut(ItemBase):
    id: int
    user_id: int
    share_key: Optional[str]=None

    model_config = ConfigDict(from_attributes=True)