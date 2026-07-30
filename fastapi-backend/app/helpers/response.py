from datetime import datetime
from typing import Any, Optional, List, Dict
from fastapi.responses import JSONResponse

from app.helpers.date_helper import get_now_wib_aware, fmt_dt, WIB_TZ


def _ensure_tz(data: Any) -> Any:
    if isinstance(data, datetime) and data.tzinfo is None:
        return data.replace(tzinfo=WIB_TZ)
    if isinstance(data, dict):
        return {k: _ensure_tz(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [_ensure_tz(v) for v in data]
    return data


def success_response(
    data: Any = None,
    message: str = "Success",
    code: int = 200,
) -> Dict:
    data = _ensure_tz(data)
    return {
        "status": "success",
        "code": code,
        "message": message,
        "data": data,
        "timestamp": fmt_dt(get_now_wib_aware()),
    }


def error_response(
    message: str = "Error",
    code: int = 400,
    errors: Optional[List[Dict[str, str]]] = None,
) -> JSONResponse:
    body: Dict[str, Any] = {
        "status": "error",
        "code": code,
        "message": message,
        "timestamp": fmt_dt(get_now_wib_aware()),
    }
    if errors:
        body["errors"] = _ensure_tz(errors)
    return JSONResponse(status_code=code, content=body) 


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    per_page: int,
    message: str = "Data retrieved successfully",
) -> Dict:
    """Standard paginated envelope."""
    total_pages = (total + per_page - 1) // per_page
    return success_response(
        data={
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
            },
        },
        message=message,
    )
