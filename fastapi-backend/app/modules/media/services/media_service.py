from sqlalchemy.orm import Session
from fastapi import UploadFile
from typing import Optional, List
import os

from app.modules.media.models.media_model import Media
from app.core.storage.manager import StorageManager
from app.modules.audit.services.audit_service import AuditService


class MediaService:
    @staticmethod
    def upload_media(
        db: Session, 
        file: UploadFile, 
        user_id: Optional[int] = None, 
        sub_dir: str = "general",
        request = None
    ) -> Media:
        """Upload file via StorageManager and track in Media table."""
        # 1. Save file to storage provider
        meta = StorageManager.save(file, sub_dir=sub_dir)
        
        # 2. Create database record
        new_media = Media(
            filename=meta["filename"],
            original_name=meta["original_name"],
            path=meta["path"],
            size=meta["size"],
            mime_type=meta["mime_type"],
            storage_mode=meta["storage_mode"],
            user_id=user_id
        )
        db.add(new_media)
        db.commit()
        db.refresh(new_media)

        # 3. Log activity
        AuditService.log(
            db=db, user_id=user_id, action="UPLOAD_MEDIA", module="MEDIA",
            item_id=str(new_media.id), description=f"Uploaded file: {meta['original_name']}",
            request=request
        )

        return new_media

    @staticmethod
    def get_media(db: Session, media_id: int) -> Optional[Media]:
        return db.query(Media).filter(Media.id == media_id).first()

    @staticmethod
    def delete_media(db: Session, media_id: int, user_id: Optional[int] = None) -> bool:
        media = MediaService.get_media(db, media_id)
        if not media:
            return False
        
        # Delete physical file
        StorageManager.delete(media.path)
        
        # Delete DB record
        db.delete(media)
        db.commit()
        
        return True
