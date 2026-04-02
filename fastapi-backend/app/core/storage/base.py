from abc import ABC, abstractmethod
from fastapi import UploadFile
from typing import Optional


class BaseStorageProvider(ABC):
    @abstractmethod
    def save(self, file: UploadFile, sub_dir: str = "", custom_name: Optional[str] = None) -> dict:
        """Save file and return metadata (path, filename, size, mime_type)."""
        pass

    @abstractmethod
    def delete(self, path: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    def get_url(self, path: str) -> str:
        """Return a publicly accessible URL or a proxy path for the file."""
        pass
