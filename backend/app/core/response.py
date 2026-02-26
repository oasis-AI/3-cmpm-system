from typing import Any
from fastapi.responses import JSONResponse


def success(data: Any = None, message: str = "success") -> JSONResponse:
    return JSONResponse(content={"code": 0, "message": message, "data": data})


def paginated(
    items: list,
    total: int,
    page: int,
    page_size: int,
) -> JSONResponse:
    return JSONResponse(
        content={
            "code": 0,
            "message": "success",
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            },
        }
    )
