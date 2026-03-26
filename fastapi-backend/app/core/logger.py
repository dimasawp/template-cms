import json
import logging
import logging.handlers
import os
import traceback
from datetime import datetime, timezone, timedelta


class JSONFormatter(logging.Formatter):
    """Outputs each log record as a single-line JSON object (JSONL)."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict = {
            "timestamp": datetime.now(tz=timezone(timedelta(hours=7))).isoformat(),
            "level": record.levelname,
        }
        for field in ("method", "path", "status_code", "client_ip",
                       "error_detail", "request_id"):
            value = getattr(record, field, None)
            if value is not None:
                log_entry[field] = value

        log_entry["message"] = record.getMessage()

        if record.exc_info and record.exc_info[0] is not None:
            log_entry["traceback"] = "".join(
                traceback.format_exception(*record.exc_info)
            )

        return json.dumps(log_entry, ensure_ascii=False, default=str)


_LOGGER_NAME = "cms_template_api"


def setup_logger(
    log_dir: str = "logs",
    max_bytes: int = 104_857_600,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Configure and return the application logger.

    - Writes WARNING / ERROR / CRITICAL entries to ``logs/error.log``
    - Rotates at *max_bytes*, keeping *backup_count* old files
    """
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.WARNING)

    handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, "error.log"),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(logging.WARNING)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.propagate = False

    return logger


def get_logger() -> logging.Logger:
    """Return the application logger (call ``setup_logger`` first)."""
    return logging.getLogger(_LOGGER_NAME)


def log_error(
    *,
    message: str,
    method: str = "",
    path: str = "",
    status_code: int = 0,
    client_ip: str = "",
    error_detail: str = "",
    request_id: str = "",
    exc_info=None,
    level: int = logging.ERROR,
):
    """Convenience helper used by the error-logging middleware."""
    get_logger().log(
        level,
        message,
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "client_ip": client_ip,
            "error_detail": error_detail,
            "request_id": request_id,
        },
        exc_info=exc_info,
    )
