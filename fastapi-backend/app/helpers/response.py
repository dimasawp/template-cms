from datetime import datetime, timezone
from typing import Any, Optional, List, Dict
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "Success",
    code: int = 200,
) -> Dict:
    """Standard JSON envelope for successful operations."""
    return {
        "status": "success",
        "code": code,
        "message": message,
        "data": data,
        "timestamp": __import__('app.helpers.date_helper', fromlist=['get_now_wib_aware']).get_now_wib_aware().isoformat(),
    }


def error_response(
    message: str = "Error",
    code: int = 400,
    errors: Optional[List[Dict[str, str]]] = None,
) -> JSONResponse:
    """Standard JSON envelope for error responses."""
    body: Dict[str, Any] = {
        "status": "error",
        "code": code,
        "message": message,
        "timestamp": __import__('app.helpers.date_helper', fromlist=['get_now_wib_aware']).get_now_wib_aware().isoformat(),
    }
    if errors:
        body["errors"] = errors

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
