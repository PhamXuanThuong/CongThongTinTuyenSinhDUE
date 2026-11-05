from typing import Dict, Any, Tuple
from portal.forms import ClubRegistrationForm


def register_club_member(data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Business service to process student club registration.
    Performs full input validation, sanitization, and returns structured status.
    """
    form = ClubRegistrationForm(data)
    if not form.is_valid():
        return False, form.errors

    cleaned = form.cleaned_data
    # Here we can persist to database if model exists or log registration
    return True, {
        "student_name": cleaned.get("ho_ten"),
        "student_id": cleaned.get("mssv"),
        "club_id": cleaned.get("cau_lac_bo_id"),
        "status": "registered_successfully"
    }

