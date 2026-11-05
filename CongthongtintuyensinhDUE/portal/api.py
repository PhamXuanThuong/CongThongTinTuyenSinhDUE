from django.http import HttpRequest, JsonResponse
from core.responses import ApiResponse, parse_json_body
from core.ratelimit import rate_limit
from portal import selectors, services


def api_faculties_list(request: HttpRequest) -> JsonResponse:
    """Returns standardized list of all faculties and departments."""
    faculties = selectors.get_faculties()
    return ApiResponse.success(data=faculties)


def api_faculty_detail(request: HttpRequest, code: str) -> JsonResponse:
    """Returns standardized detail info for one faculty."""
    faculty = selectors.get_faculty_by_code(code)
    if not faculty:
        return ApiResponse.error(message="Faculty not found", status=404, code="NOT_FOUND")
    return ApiResponse.success(data=faculty)


def api_clubs_list(request: HttpRequest) -> JsonResponse:
    """Returns standardized list of all student clubs."""
    clubs = selectors.get_clubs()
    return ApiResponse.success(data=clubs)


@rate_limit(key_prefix="club_reg", max_requests=5, timeout_seconds=60)
def api_club_register(request: HttpRequest) -> JsonResponse:
    """Handles club registration with rate-limiting and validation."""
    if request.method != "POST":
        return ApiResponse.error(message="Method not allowed", status=405, code="METHOD_NOT_ALLOWED")
    
    data = parse_json_body(request)
    if not data and request.POST:
        data = request.POST.dict()

    success, result = services.register_club_member(data)
    if not success:
        return ApiResponse.error(
            message="Invalid registration data",
            errors=result,
            status=400,
            code="VALIDATION_ERROR"
        )
    return ApiResponse.success(data=result, message="Đăng ký câu lạc bộ thành công!")

