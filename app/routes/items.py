from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas, security
from app.config import get_db
from app.mega_service import mega_storage

router = APIRouter(prefix="/api/v1/items", tags=["items"])

@router.get("", response_model=List[schemas.ItemResponse])
def get_user_items(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    return db.query(models.Item).filter(models.Item.user_id == current_user.id).order_by(models.Item.created_at.desc()).all()

@router.post("", response_model=schemas.ItemResponse)
def create_text_item(
    item_in: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    new_item = models.Item(
        user_id=current_user.id,
        item_type=item_in.item_type,
        title=item_in.title,
        content=item_in.content
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.post("/upload", response_model=schemas.ItemResponse)

def upload_file_item(
    title: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    # Determine type (image vs general file)
    is_image = file.content_type and file.content_type.startswith("image/")
    item_type = "image" if is_image else "file"

    # Upload to MEGA
    mega_url = mega_storage.upload_file(file)

    # Save metadata to DB
    new_item = models.Item(
        user_id=current_user.id,
        item_type=item_type,
        title=title or file.filename,
        content=file.filename,
        file_path=mega_url,
        file_type=file.content_type,
        file_size=file.size
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    item = db.query(models.Item).filter(models.Item.id == item_id, models.Item.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return None