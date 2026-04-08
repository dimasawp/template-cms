import os
import shutil
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import UploadFile, HTTPException

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
        filename = custom_name or f"{uuid.uuid4().hex}_{int(get_now_wib().timestamp())}.{ext}"
        
        target_dir = os.path.join(self.base_dir, sub_dir) if sub_dir else self.base_dir
        os.makedirs(target_dir, exist_ok=True)
        
        dest_path = os.path.join(target_dir, filename)
        
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
            "mime_type": file.content_type,
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
