from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class SettingBase(BaseModel):
    setting_key: str
    setting_value: Optional[str] = None
    description: Optional[str] = None


class SettingCreate(SettingBase):
    pass


class SettingUpdate(BaseModel):
    setting_value: Optional[str] = None
    description: Optional[str] = None


class SettingResponse(SettingBase):
    id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SettingBulkUpdate(BaseModel):
    settings: List[SettingBase]
