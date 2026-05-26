from sqlalchemy.orm import Session
from app.modules._base.repository import BaseRepository
from app.modules.categories.models.category_model import Category

class CategoryRepository(BaseRepository):
    model = Category
    search_fields = ["name", "slug"]

    @classmethod
    def get_by_slug(cls, db: Session, slug: str):
        return db.query(Category).filter(Category.slug == slug).first()
