from typing import Any, Optional
from app.common.schemas.response_schemas import Response


def success_response(message: str, data: Any = None) -> Response:
    return Response(
        success=True,
        message=message,
        data=data,
        errors=None
    )


def error_response(message: str, errors: Optional[Any] = None) -> Response:
    return Response(
        success=False,
        message=message,
        data=None,
        errors=errors
    )
