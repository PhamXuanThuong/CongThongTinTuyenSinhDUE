from typing import List, Dict, Any, Optional
from portal.models import Faculty, Department
from admissions.models import CauLacBo

FACULTY_NAMES: Dict[str, str] = {
    'tcnh': 'Khoa Tài chính - Ngân hàng',
    'dlkdqt': 'Khoa Du lịch và kinh doanh quốc tế',
    'tmdt_mkt_cns': 'Khoa Thương mại điện tử - Marketing và Công nghệ số',
    'kt': 'Khoa Kinh tế',
    'qtkd': 'Khoa Quản trị kinh doanh',
    'ketoan': 'Khoa Kế toán',
    'llct': 'Khoa Lý luận chính trị',
    'luat': 'Khoa Luật',
    'vdtqt': 'Viện Đào tạo Quốc tế',
}


def get_departments() -> List[Dict[str, Any]]:
    """Loads all university administrative and functional departments directly from database."""
    departments = Department.objects.filter(is_active=True).order_by('order', 'id')
    return [d.to_dict() for d in departments]


def get_faculties() -> List[Dict[str, Any]]:
    """Loads and formats all faculty and institute records directly from database."""
    faculties = Faculty.objects.filter(is_active=True).order_by('order', 'id')
    return [f.to_dict() for f in faculties]


def get_faculty_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Finds a faculty by code or aliases from database."""
    clean_code = code.strip().rstrip('/').lower()

    # Thử tìm trực tiếp theo code
    faculty = Faculty.objects.filter(code__iexact=clean_code, is_active=True).first()
    if faculty:
        return faculty.to_dict()

    # Thử tìm dạng gạch dưới hoặc gạch nối
    norm_code = clean_code.replace('-', '_')
    faculty = Faculty.objects.filter(code__iexact=norm_code, is_active=True).first()
    if faculty:
        return faculty.to_dict()

    alt_norm_code = clean_code.replace('_', '-')
    faculty = Faculty.objects.filter(code__iexact=alt_norm_code, is_active=True).first()
    if faculty:
        return faculty.to_dict()

    # Nếu không tìm thấy bằng code chính, quét qua danh sách aliases
    for f in Faculty.objects.filter(is_active=True):
        aliases = [str(a).lower() for a in (f.aliases or [])]
        if clean_code in aliases or norm_code in aliases:
            return f.to_dict()

    return None


def get_clubs() -> List[Dict[str, Any]]:
    """Loads clubs from database."""
    db_clubs = list(CauLacBo.objects.filter(is_active=True).order_by('order', 'id'))
    return [c.to_dict() for c in db_clubs]


def get_club_by_id(club_id: str) -> Optional[Dict[str, Any]]:
    """Finds club by slug or alias directly from database."""
    clean_id = club_id.strip().rstrip('/')
    # Thử tìm theo slug trước
    club = CauLacBo.objects.filter(slug__iexact=clean_id, is_active=True).first()
    if club:
        return club.to_dict()

    # Tìm trong aliases
    for c in CauLacBo.objects.filter(is_active=True):
        aliases = [str(a).lower() for a in (c.aliases or [])]
        if clean_id.lower() in aliases:
            return c.to_dict()

    return None
