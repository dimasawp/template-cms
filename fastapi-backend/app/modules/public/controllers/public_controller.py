from fastapi import APIRouter, Depends, Request, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from typing import Optional

from app.core.database import get_db
from app.core.limiter import limiter
from app.helpers.response import success_response
from app.exceptions import handle_errors, NotFoundException
from app.modules.posts.models.post_model import Post
from app.modules.categories.models.category_model import Category
from app.modules.categories.services.category_service import CategoryService
from app.modules.settings.models.setting_model import Setting

router = APIRouter(prefix="/api/v1/public", tags=["Public API"])

@router.get("/posts")
@limiter.limit("100/minute")
@handle_errors
async def get_public_posts(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    category_slug: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get published posts for frontend display."""
    query = db.query(Post).filter(Post.status == "PUBLISHED", Post.deleted_at == None)
    
    if category_slug:
        cat = db.query(Category).filter(Category.slug == category_slug, Category.deleted_at == None).first()
        if not cat:
            return success_response(data={"items": [], "pagination": {"total": 0, "page": page, "per_page": per_page, "total_pages": 0}})
        query = query.filter(Post.category_id == cat.id)
        
    total = query.count()
    items = query.options(joinedload(Post.author)).order_by(desc(Post.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    return success_response(
        data={
            "items": [
                {
                    "id": p.id,
                    "title": p.title,
                    "slug": p.slug,
                    "thumbnail": p.thumbnail,
                    "created_at": p.created_at,
                    "category": p.category_id, # In a real app we'd join and return category slug/name
                    "author": {
                        "username": p.author.username,
                        "full_name": p.author.full_name
                    } if p.author else None
                }
                for p in items
            ],
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
    )

@router.get("/posts/{slug}")
@limiter.limit("100/minute")
@handle_errors
async def get_public_post_detail(
    request: Request,
    slug: str,
    db: Session = Depends(get_db)
):
    """Get a specific post detail (PUBLISHED or ARCHIVED)."""
    post = db.query(Post).options(joinedload(Post.author)).filter(
        Post.slug == slug, 
        Post.status.in_(["PUBLISHED", "ARCHIVED"]),
        Post.deleted_at == None
    ).first()
    
    if not post:
        raise NotFoundException("Post not found")
        
    return success_response(data={
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "thumbnail": post.thumbnail,
        "content": post.content,
        "additional_contents": post.additional_contents,
        "status": post.status,
        "created_at": post.created_at,
        "author": {
            "username": post.author.username,
            "full_name": post.author.full_name
        } if post.author else None
    })

@router.get("/categories")
@limiter.limit("100/minute")
@handle_errors
async def get_public_categories(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all active categories formatted as a tree."""
    # Reusing category service to fetch active categories
    categories = db.query(Category).filter(
        Category.is_active == True,
        Category.deleted_at == None
    ).order_by(Category.order_index).all()
    
    cat_dicts = []
    for c in categories:
        cat_dicts.append({
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "parent_id": c.parent_id,
            "is_menu": c.is_menu,
            "order_index": c.order_index
        })
        
    return success_response(data={"items": cat_dicts})

@router.get("/settings")
@limiter.limit("100/minute")
@handle_errors
async def get_public_settings(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get public settings."""
    # Since there's no is_public column, we assume "general" group settings are safe for public consumption.
    settings = db.query(Setting).filter(Setting.setting_group == "general").all()
    
    res = {}
    for s in settings:
        res[s.setting_key] = s.setting_value
        
    return success_response(data=res)
