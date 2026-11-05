from typing import Dict, Any, Tuple, Optional
from tuyensinh.forms import CounselingRegistrationForm, TuitionCalculationForm
from tuyensinh.models import TuVanTuyenSinh
from tuyensinh.selectors import find_tuition_rate
from core.responses import ApiResponse
from core.sanitization import sanitize_text


def calculate_tuition(params: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Calculates year and term tuition in VND."""
    form = TuitionCalculationForm(params)
    if not form.is_valid():
        return False, {"message": "Dữ liệu tính toán không hợp lệ"}

    slug = form.cleaned_data.get('slug')
    year_index = form.cleaned_data.get('year', 0)

    tuition = find_tuition_rate(slug)
    if not tuition:
        return False, {"message": "Không tìm thấy thông tin chương trình"}

    rates = [tuition.nam_hoc_1, tuition.nam_hoc_2, tuition.nam_hoc_3, tuition.nam_hoc_4]
    year_idx = max(0, min(year_index, len(rates) - 1))
    mil = float(rates[year_idx])
    year_vnd = int(mil * 1_000_000)
    term_vnd = int(year_vnd / 2)

    return True, {
        "program": tuition.nhom,
        "year_vnd": year_vnd,
        "term_vnd": term_vnd,
        "year_vnd_formatted": f"{year_vnd:,.0f}".replace(",", "."),
        "term_vnd_formatted": f"{term_vnd:,.0f}".replace(",", ".")
    }


def register_counseling(data: Dict[str, Any]) -> Tuple[bool, Any]:
    """Processes counseling registration and persists record."""
    form = CounselingRegistrationForm(data)
    if not form.is_valid():
        return False, form.errors

    cleaned = form.cleaned_data
    record = TuVanTuyenSinh.objects.create(
        ho_ten=cleaned['ho_ten'],
        so_dien_thoai=cleaned['so_dien_thoai'],
        email=cleaned['email'],
        nganh_quan_tam=cleaned.get('nganh_quan_tam', ''),
        noi_dung_cau_hoi=cleaned.get('noi_dung_cau_hoi', ''),
        trang_thai='cho_xu_ly'
    )
    return True, record

