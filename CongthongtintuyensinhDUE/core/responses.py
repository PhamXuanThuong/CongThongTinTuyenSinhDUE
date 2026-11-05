import json
from functools import wraps
from typing import Any, Dict, Optional
from django.http import JsonResponse, HttpRequest, HttpResponse


class ApiResponse:
    """
    Standardized API Response Envelope for Django APIs.
    Guarantees consistent schema across all endpoints:
    {
        "success": bool,
        "message": str,
        "data": Optional[Any],
        "errors": Optional[Any],
        "meta": Optional[Dict[str, Any]]
    }
    """

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation completed successfully",
        status: int = 200,
        meta: Optional[Dict[str, Any]] = None,
    ) -> JsonResponse:
        payload = {
            "success": True,
            "message": message,
            "data": data,
            "errors": None,
        }
        if meta is not None:
            payload["meta"] = meta
        return JsonResponse(payload, status=status)

    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Any = None,
        status: int = 400,
        code: Optional[str] = None,
    ) -> JsonResponse:
        payload = {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors if errors is not None else message,
        }
        if code:
            payload["code"] = code
        return JsonResponse(payload, status=status)


def parse_json_body(request: HttpRequest) -> Dict[str, Any]:
    """
    Safely parses JSON request body into a python dict.
    Returns empty dict if payload is empty or invalid.
    """
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}

