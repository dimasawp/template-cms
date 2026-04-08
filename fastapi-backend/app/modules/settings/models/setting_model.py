from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core.database import Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    setting_key = Column(String(100), nullable=False, unique=True, index=True)
    setting_value = Column(Text, nullable=True)
    description = Column(String(255), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: __import__('app.helpers.date_helper', fromlist=['get_now_wib']).get_now_wib(),
        onupdate=lambda: __import__('app.helpers.date_helper', fromlist=['get_now_wib']).get_now_wib(),
        nullable=False,
    )
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Setting {self.setting_key}={self.setting_value}>"
