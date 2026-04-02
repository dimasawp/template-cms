from fastapi import APIRouter, Depends, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.models.user_model import User
from app.modules.media.services.media_service import MediaService
from app.helpers.response import success_response, error_response
from app.exceptions import handle_errors


router = APIRouter(prefix="/api/v1/media", tags=["Media"])


@router.post("/upload")
@handle_errors
async def upload_media(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a file to the configured storage provider."""
    media = MediaService.upload_media(
        db, file, user_id=current_user.id, request=request
    )
    return success_response(
        data={
            "id": media.id,
            "filename": media.filename,
            "original_name": media.original_name,
            "path": media.path,
            "storage_mode": media.storage_mode
        },
        message="File uploaded successfully"
    )


@router.get("/view")
async def view_media(
    path: str,
    db: Session = Depends(get_db),
    # Optional: current_user: User = Depends(get_current_user)
):
    """View/Download media file via proxy (useful for local_system storage)."""
    # Security check: Ensure the path is part of our media records
    # (Simple check for now: path must exist and not be a directory)
    if not os.path.isfile(path):
         raise HTTPException(status_code=404, detail="File not found or access denied")
    
    # We could check permissions here based on DB records
    # For now, we serve it as a file
    return FileResponse(path)
