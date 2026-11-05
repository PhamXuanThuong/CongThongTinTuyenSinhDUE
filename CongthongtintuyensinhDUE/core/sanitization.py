import html
import re
from typing import Optional, Union


def sanitize_text(text: Optional[str]) -> str:
    """
    Strips dangerous characters and escapes HTML tags to prevent XSS.
    Safe for plain text storage and rendering.
    """
    if not text:
        return ""
    # Strip null bytes and control characters
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", str(text))
    # Escape HTML special characters
    return html.escape(cleaned.strip())


def sanitize_alphanumeric(text: Optional[str], extra_allowed: str = "-_") -> str:
    """
    Ensures input only contains alphanumeric characters plus allowed symbols (for slugs, codes, ids).
    """
    if not text:
        return ""
    pattern = rf"[^a-zA-Z0-9{re.escape(extra_allowed)}]"
    return re.sub(pattern, "", str(text)).strip()

