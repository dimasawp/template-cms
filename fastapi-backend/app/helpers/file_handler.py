"""
File upload / storage helper.
"""

import os
import uuid
import shutil
from datetime import datetime, timezone
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings


def _ensure_upload_dir(sub: str = "") -> str:
    path = os.path.join(settings.UPLOAD_DIR, sub) if sub else settings.UPLOAD_DIR
    os.makedirs(path, exist_ok=True)
    return path


def validate_file(file: UploadFile) -> None:
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{ext}' not allowed. "
                   f"Allowed: {', '.join(settings.allowed_extensions_list)}",
        )


def save_file(
    file: UploadFile,
    sub_dir: str = "",
    custom_name: Optional[str] = None,
) -> str:
    validate_file(file)
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "bin"
    filename = custom_name or f"{uuid.uuid4().hex}_{int(datetime.now(timezone.utc).timestamp())}.{ext}"
    dest_dir = _ensure_upload_dir(sub_dir)
    dest = os.path.join(dest_dir, filename)

    with open(dest, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    return os.path.relpath(dest).replace("\\", "/")


def delete_file(path: str) -> bool:
    if os.path.isfile(path):
        os.remove(path)
        return True
    return False
