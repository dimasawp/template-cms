from sqlalchemy.orm import Session

from app.modules._base.repository import BaseRepository
from app.modules.users.models.user_model import User


class UserRepository(BaseRepository):
    model = User
    search_fields = ["username", "email", "full_name"]

    @classmethod
    def get_by_username(cls, db: Session, username: str):
        return db.query(User).filter(User.username == username).first()
