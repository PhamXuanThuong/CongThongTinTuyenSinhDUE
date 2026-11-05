import time
from functools import wraps
from typing import Callable
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from core.responses import ApiResponse


def get_client_ip(request: HttpRequest) -> str:
    """Extract client IP safely taking proxies into account."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def rate_limit(key_prefix: str = "rl", max_requests: int = 15, timeout_seconds: int = 60):
    """
    Django in-memory / cache-backed rate limiting decorator.
    Usage:
        @rate_limit(key_prefix="chatbot", max_requests=10, timeout_seconds=60)
        def my_view(request):
            ...
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            ip = get_client_ip(request)
            user_id = request.user.id if request.user.is_authenticated else "anon"
            cache_key = f"rate_limit:{key_prefix}:{ip}:{user_id}"

            history = cache.get(cache_key, [])
            now = time.time()
            # Retain only timestamps within the time window
            valid_history = [ts for ts in history if now - ts < timeout_seconds]

            if len(valid_history) >= max_requests:
                retry_after = int(timeout_seconds - (now - valid_history[0]))
                return ApiResponse.error(
                    message=f"Rate limit exceeded. Please wait {max(1, retry_after)} seconds before trying again.",
                    errors={"rate_limit": "Too Many Requests"},
                    status=429,
                    code="RATE_LIMIT_EXCEEDED"
                )

            valid_history.append(now)
            cache.set(cache_key, valid_history, timeout=timeout_seconds)
            return view_func(request, *args, **kwargs)

        return wrapped_view
    return decorator

