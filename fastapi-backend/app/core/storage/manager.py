from typing import Optional
from fastapi import UploadFile

from app.core.config import settings
from app.core.storage.base import BaseStorageProvider
from app.core.storage.local_project import LocalProjectProvider
from app.core.storage.local_system import LocalSystemProvider


class StorageManager:
    _instance: Optional[BaseStorageProvider] = None

    @classmethod
    def get_provider(cls) -> BaseStorageProvider:
        if cls._instance is None:
            mode = settings.STORAGE_MODE
            
            if mode == "local_system":
                cls._instance = LocalSystemProvider()
            elif mode == "cloud":
                # For future: implement S3Provider()
                # For now, fallback or raise error
                cls._instance = LocalProjectProvider()
            else:
                cls._instance = LocalProjectProvider()
                
        return cls._instance

    @staticmethod
    def save(file: UploadFile, sub_dir: str = "", custom_name: Optional[str] = None) -> dict:
        return StorageManager.get_provider().save(file, sub_dir, custom_name)

    @staticmethod
    def delete(path: str) -> bool:
        return StorageManager.get_provider().delete(path)

    @staticmethod
    def get_url(path: str, storage_mode: str = "local_project") -> str:
        # If we know the mode used for the file, we can get the correct provider instance
        # However, for simple cases, get_provider() uses current global setting
        return StorageManager.get_provider().get_url(path)
