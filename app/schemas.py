from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


# --- User Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



# --- Item Schemas ---
class ItemBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None  # Text note content OR URL link


class ItemCreate(ItemBase):
    item_type: str  # 'text' or 'link'


class ItemResponse(ItemBase):
    id: int
    user_id: int
    item_type: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Auth Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[int] = None


