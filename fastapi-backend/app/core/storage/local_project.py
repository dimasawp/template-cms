import os
import shutil
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image

from app.core.config import settings
from app.core.storage.base import BaseStorageProvider


class LocalProjectProvider(BaseStorageProvider):
    def __init__(self):
        self.base_dir = settings.UPLOAD_DIR
        os.makedirs(self.base_dir, exist_ok=True)

    def save(self, file: UploadFile, sub_dir: str = "", custom_name: Optional[str] = None) -> dict:
        # Validate extensions (logic from old file_handler)
        ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "bin"
        if ext not in settings.allowed_extensions_list:
            raise HTTPException(status_code=400, detail=f"Extension '{ext}' not allowed")

        from app.helpers.date_helper import get_now_wib
        now = get_now_wib()
        year_month = now.strftime("%Y/%m")
        
        filename = custom_name or f"{uuid.uuid4().hex}_{int(now.timestamp())}.{ext}"
        
        final_sub_dir = os.path.join(sub_dir, year_month) if sub_dir else year_month
        target_dir = os.path.join(self.base_dir, final_sub_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        dest_path = os.path.join(target_dir, filename)
        mime_type = file.content_type
        
        if mime_type and mime_type.startswith("image/") and ext in ["jpg", "jpeg", "png", "bmp"]:
            try:
                img = Image.open(file.file)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")
                    
                new_filename = filename.rsplit(".", 1)[0] + ".webp"
                dest_path = os.path.join(target_dir, new_filename)
                
                # Auto-resize to max 1920x1920 (maintains aspect ratio)
                max_size = (1920, 1920)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                img.save(dest_path, "WEBP", quality=80)
                
                size = os.path.getsize(dest_path)
                filename = new_filename
                mime_type = "image/webp"
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")
        else:
            # Read file size
            file.file.seek(0, os.SEEK_END)
            size = file.file.tell()
            file.file.seek(0)

            with open(dest_path, "wb") as buf:
                shutil.copyfileobj(file.file, buf)

        # Return metadata for database
        relative_path = os.path.relpath(dest_path, os.getcwd()).replace("\\", "/")
        return {
            "filename": filename,
            "original_name": file.filename,
            "path": relative_path,
            "size": size,
            "mime_type": mime_type,
            "storage_mode": "local_project"
        }

    def delete(self, path: str) -> bool:
        if os.path.isfile(path):
            os.remove(path)
            return True
        return False

    def get_url(self, path: str) -> str:
        # Assuming backend serves files from /storage or similar
        # For now, we return the relative path
        return path
