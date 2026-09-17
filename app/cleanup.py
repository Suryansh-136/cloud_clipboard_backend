from datetime import datetime, timedelta, timezone
from app.config import SessionLocal
from app.models import Item
from app.mega_service import mega_storage

def delete_expired_items():
    db = SessionLocal()
    try:
        # Calculate time threshold (24 hours ago)
        threshold = datetime.now(timezone.utc) - timedelta(hours=24)
        
        # Query items older than 24 hours
        expired_items = db.query(Item).filter(Item.created_at <= threshold).all()
        
        if not expired_items:
            return

        print(f"[Cleanup] Found {len(expired_items)} expired items. Purging...")
        
        for item in expired_items:
            # Delete file payload from MEGA if applicable
            if item.file_path:
                mega_storage.delete_file_by_url(item.file_path)
            
            # Remove database metadata record
            db.delete(item)

        db.commit()
        print("[Cleanup] Expired items successfully removed.")
    except Exception as e:
        print(f"[Cleanup] Error during cleanup execution: {e}")
    finally:
        db.close()