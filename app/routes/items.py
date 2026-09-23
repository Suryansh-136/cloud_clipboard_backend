from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
import urllib.parse
from app.config import get_db
from app.mega_service import mega_storage
from app.models import Item, User
from app.schemas import ItemCreate, ItemResponse
from app.security import get_current_user

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=List[ItemResponse])
def get_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Item).filter(Item.user_id == current_user.id).all()


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_item = Item(
        content_type=item_in.content_type,
        text_payload=item_in.text_payload,
        file_path=item_in.file_path,
        user_id=current_user.id,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.post("/upload", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def upload_file_item(
    title: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Determine type (image vs general file)
    is_image = file.content_type and file.content_type.startswith("image/")
    content_type = "image" if is_image else "file"

    # Upload to MEGA storage
    mega_url = mega_storage.upload_file(file)

    # Save metadata to DB using matching schema fields
    new_item = Item(
        user_id=current_user.id,
        content_type=content_type,
        text_payload=title or file.filename,
        file_path=mega_url,
        file_size=file.size if hasattr(file, "size") else None,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(Item)
        .filter(Item.id == item_id, Item.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    db.delete(item)
    db.commit()
    return None


@router.get("/api/v1/items/{item_id}/download")
def download_item(item_id: int, db=Depends(get_db)):
    # 1. PostgreSQL DB se file record uthao
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="File not found")

    # 2. Filename encoding handle karein (special characters ke liye)
    encoded_filename = urllib.parse.quote(item.file_name)

    # 3. FastAPI StreamingResponse return karein
    return StreamingResponse(
        mega_service.download_file_stream(item.mega_handle),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )