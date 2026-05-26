from sqlalchemy.orm import Session
from app.modules._base.repository import BaseRepository
from app.modules.posts.models.post_model import Post

class PostRepository(BaseRepository):
    model = Post
    search_fields = ["title", "slug"]

    @classmethod
    def get_by_slug(cls, db: Session, slug: str):
        return db.query(Post).filter(Post.slug == slug).first()
