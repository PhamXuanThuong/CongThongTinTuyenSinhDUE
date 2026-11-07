"""Cấu hình riêng cho bộ kiểm thử: CSDL tạm trong bộ nhớ, tắt khóa AI để không gọi mạng."""
from .settings import *  # noqa

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
GEMINI_API_KEY = ""
OLLAMA_BASE_URL = "http://127.0.0.1:9"
