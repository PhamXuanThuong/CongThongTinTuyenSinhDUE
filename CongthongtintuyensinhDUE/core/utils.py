import re
import unicodedata
from typing import Any, Dict


def slugify_vietnamese(text: str) -> str:
    """
    Standard slug generator supporting Vietnamese diacritics.
    Replaces special characters and produces clean URL slugs.
    """
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    # Replace 'đ' and 'Đ'
    text = re.sub(r"[đĐ]", "d", text)
    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def format_currency_vnd(amount: Any) -> str:
    """
    Helper to format numbers into standard Vietnamese currency string (e.g. 15.000.000 đ).
    """
    try:
        val = int(amount)
        return f"{val:,}".replace(",", ".") + " đ"
    except (ValueError, TypeError):
        return "0 đ"

