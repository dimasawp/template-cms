from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ─── Application ────────────────────────────────────────────────
    APP_NAME: str = "CMS Template API"
    APP_VERSION: str = "1.1.0"
    ENV: str = "development"  # development | staging | production
    DEBUG: bool = False
    ENABLE_WEBSOCKETS: bool = True

    # ─── Database ───────────────────────────────────────────────────
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "db_cms_template"

    # ─── JWT ────────────────────────────────────────────────────────
    SECRET_KEY: str = "CHANGE_ME_TO_RANDOM_SECRET"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── File Upload ────────────────────────────────────────────────
    MAX_FILE_SIZE: int = 10485760  # 10 MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,gif,webp,pdf,xlsx,docx,csv"
    UPLOAD_DIR: str = "storage/uploads"
    
    # storage_mode: 'local_project' | 'local_system' | 'cloud'
    STORAGE_MODE: str = "local_project"
    # system_storage_path: used when STORAGE_MODE is 'local_system' (absolute path)
    SYSTEM_STORAGE_PATH: str = "C:/CMS_STORAGE"

    # ─── Email (SMTP) ──────────────────────────────────────────────
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "no-reply@example.com"
    SMTP_FROM_NAME: str = "CMS Template"
    SMTP_USE_TLS: bool = False

    # ─── Logging ────────────────────────────────────────────────────
    LOG_DIR: str = "logs"
    LOG_MAX_BYTES: int = 104857600  # 100 MB
    LOG_BACKUP_COUNT: int = 5

    # ─── CORS ───────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # ─── Computed properties ────────────────────────────────────────
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
