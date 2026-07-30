from fastapi import APIRouter, Depends, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.modules.users.models.user_model import User
from app.modules.media.services.media_service import MediaService
from app.helpers.response import success_response, error_response
from app.exceptions import handle_errors


router = APIRouter(prefix="/api/v1/media", tags=["Media"])


@router.post("/upload")
@handle_errors
async def upload_media(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("media.create")),
):
    """Upload a file to the configured storage provider."""
    form = await request.form()
    
    file = form.get("file") or form.get("files[0]") or form.get("files")
    
    if not file or not hasattr(file, "filename"):
        keys = list(form.keys())
        raise HTTPException(status_code=400, detail=f"No valid file uploaded. Keys: {keys}, Type: {type(file).__name__}")
        
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
@handle_errors
async def view_media(
    path: str,
    db: Session = Depends(get_db),
    _current_user: User = Depends(check_permission("media.view")),
):
    """View/Download media file via proxy (requires media.view permission)."""
    if not os.path.isfile(path):
         raise HTTPException(status_code=404, detail="File not found or access denied")
    
    return FileResponse(path)

@router.get("")
@router.get("/")
@handle_errors
async def get_all_media(
    skip: int = 0,
    limit: int = 50,
    search: str = None,
    file_type: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    user_id: int = None,
    db: Session = Depends(get_db),
    _current_user: User = Depends(check_permission("media.view"))
):
    """Get a list of all uploaded media (Requires media.view permission)."""
    total, items = MediaService.get_all_media(
        db, skip=skip, limit=limit, search=search, 
        file_type=file_type, sort_by=sort_by, sort_order=sort_order,
        user_id=user_id
    )
    return success_response(
        data={
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [
                {
                    "id": item.id,
                    "filename": item.filename,
                    "original_name": item.original_name,
                    "path": item.path,
                    "size": item.size,
                    "mime_type": item.mime_type,
                    "storage_mode": item.storage_mode,
                    "created_at": item.created_at,
                    "user": {
                        "id": item.user.id,
                        "username": item.user.username,
                        "full_name": item.user.full_name
                    } if item.user else None
                }
                for item in items
            ]
        },
        message="Media retrieved successfully"
    )

@router.delete("/{media_id}")
@handle_errors
async def delete_media(
    media_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("media.delete"))
):
    """Delete a media file (Requires media.delete permission)."""
    success = MediaService.delete_media(db, media_id=media_id, user_id=current_user.id, request=request)
    if not success:
        raise HTTPException(status_code=404, detail="Media not found or already deleted")
    
    return success_response(message="Media deleted successfully")

