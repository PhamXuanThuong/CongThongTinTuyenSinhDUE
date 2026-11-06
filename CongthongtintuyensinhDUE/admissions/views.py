import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from core.ratelimit import rate_limit

from .models import (
    TinTuc,
    LoaiHinhDaoTao,
    NganhDaoTao,
    DiemChuan,
    PhuongThucXetTuyen,
    CauHoiThuongGap,
    TuVanTuyenSinh,
    HoSoHuongNghiep,
    BangHocPhi,
    CauHoiHocPhi,
    TaiLieuTuyenSinh,
    CauHoiChoTraLoi,
)
from . import rag


def home_view(request):
    """Trang chủ Cổng thông tin Tuyển sinh DUE."""
    tin_tuc_list = TinTuc.objects.filter(noi_bat=True)[:6]
    nganh_list = NganhDaoTao.objects.all()[:8]
    loai_hinh_list = LoaiHinhDaoTao.objects.all().order_by('thu_tu')
    phuong_thuc_list = PhuongThucXetTuyen.objects.all().order_by('thu_tu')
    
    tong_chi_tieu = NganhDaoTao.objects.aggregate(total=Sum('chi_tieu'))['total'] or 4600
    tong_so_nganh = NganhDaoTao.objects.count()
    
    context = {
        'tin_tuc_list': tin_tuc_list,
        'nganh_list': nganh_list,
        'loai_hinh_list': loai_hinh_list,
        'phuong_thuc_list': phuong_thuc_list,
        'tong_chi_tieu': tong_chi_tieu,
        'tong_so_nganh': tong_so_nganh,
    }
    return render(request, 'admissions/home.html', context)


def history_view(request):
    """Trang Lịch sử phát triển DUE (Chuyến tàu 50 năm)."""
    return render(request, 'admissions/history.html')


def mission_vision_view(request):
    """Trang Sứ mệnh và tầm nhìn DUE."""
    return render(request, 'admissions/mission_vision.html')


def admission_methods_view(request):
    """Trang Phương thức xét tuyển đại học chính quy năm 2026 - DUE."""
    phuong_thuc_list = PhuongThucXetTuyen.objects.all().order_by('thu_tu')
    return render(request, 'admissions/admission_methods.html', {'phuong_thuc_list': phuong_thuc_list})


def benchmarks_view(request):
    """Trang Tra cứu Điểm chuẩn các năm (2022 - 2025) - DUE."""
    diem_chuan_list = DiemChuan.objects.select_related('nganh').all().order_by('-nam', 'nganh__ma_nganh')
    nam_list = DiemChuan.objects.values_list('nam', flat=True).distinct().order_by('-nam')
    
    context = {
        'diem_chuan_list': diem_chuan_list,
        'nam_list': nam_list,
    }
    return render(request, 'admissions/benchmarks.html', context)


def admission_quota_view(request):
    """Trang Chỉ tiêu tuyển sinh đại học năm 2026 - DUE."""
    nganh_toan_phan = NganhDaoTao.objects.filter(loai_hinh__ma_loai_hinh='toan_phan')
    nganh_ban_phan = NganhDaoTao.objects.filter(loai_hinh__ma_loai_hinh='ban_phan')
    nganh_tieu_chuan = NganhDaoTao.objects.filter(loai_hinh__ma_loai_hinh='tieu_chuan')
    tong_chi_tieu = NganhDaoTao.objects.aggregate(total=Sum('chi_tieu'))['total'] or 4600

    context = {
        'nganh_toan_phan': nganh_toan_phan,
        'nganh_ban_phan': nganh_ban_phan,
        'nganh_tieu_chuan': nganh_tieu_chuan,
        'tong_chi_tieu': tong_chi_tieu,
    }
    return render(request, 'admissions/admission_quota.html', context)


def training_programs_view(request):
    """Trang 3 Loại hình đào tạo đại học chính quy năm 2026 - DUE."""
    loai_hinh_list = LoaiHinhDaoTao.objects.prefetch_related('nganh_hoc').all().order_by('thu_tu')
    return render(request, 'admissions/training_programs.html', {'loai_hinh_list': loai_hinh_list})


def login_view(request):
    """Xử lý Đăng nhập Cổng thông tin Tuyển sinh DUE."""
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1'

    if request.user.is_authenticated:
        if is_ajax:
            redirect_url = '/admin/' if request.user.is_staff else ''
            return JsonResponse({
                'status': 'success',
                'message': f'Bạn đã đăng nhập với tài khoản {request.user.username}.',
                'redirect_url': redirect_url
            })
        if request.user.is_staff:
            return redirect('/admin/')
        return redirect('admissions:home')

    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        remember_me = request.POST.get('remember_me')

        if not username or not password:
            msg = "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!"
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': msg}, status=400)
            error_message = msg
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(1209600)

                success_msg = f"Đăng nhập thành công! Xin chào {user.first_name or user.username}."
                messages.success(request, success_msg)
                
                next_url = request.GET.get('next') or request.POST.get('next')
                redirect_url = next_url or ('/admin/' if user.is_staff else '')
                
                if is_ajax:
                    return JsonResponse({
                        'status': 'success',
                        'message': success_msg,
                        'redirect_url': redirect_url,
                        'user': {
                            'username': user.username,
                            'name': user.first_name or user.username,
                            'is_staff': user.is_staff
                        }
                    })

                if redirect_url:
                    return redirect(redirect_url)
                return redirect('admissions:home')
            else:
                msg = "Tên đăng nhập hoặc mật khẩu không chính xác. Vui lòng kiểm tra lại!"
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': msg}, status=400)
                error_message = msg

    return render(request, 'auth/login.html', {'error_message': error_message})


def logout_view(request):
    """Đăng xuất khỏi hệ thống."""
    auth_logout(request)
    messages.info(request, "Bạn đã đăng xuất khỏi Cổng thông tin Tuyển sinh DUE.")
    return redirect('admissions:home')


@csrf_exempt
def counseling_request_view(request):
    """Tiếp nhận đăng ký tư vấn tuyển sinh từ thí sinh/phụ huynh."""
    if request.method == 'POST':
        ho_ten = request.POST.get('ho_ten', '').strip()
        so_dien_thoai = request.POST.get('so_dien_thoai', '').strip()
        email = request.POST.get('email', '').strip()
        nganh_quan_tam = request.POST.get('nganh_quan_tam', '').strip()
        noi_dung_cau_hoi = request.POST.get('noi_dung_cau_hoi', '').strip()

        if not ho_ten or not so_dien_thoai:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Vui lòng cung cấp đầy đủ Họ tên và Số điện thoại liên hệ!'
                }, status=400)
            messages.error(request, 'Vui lòng điền đầy đủ họ tên và số điện thoại!')
            return redirect('admissions:home')

        yeu_cau = TuVanTuyenSinh.objects.create(
            ho_ten=ho_ten,
            so_dien_thoai=so_dien_thoai,
            email=email,
            nganh_quan_tam=nganh_quan_tam,
            noi_dung_cau_hoi=noi_dung_cau_hoi,
            trang_thai='cho_xu_ly'
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'Cảm ơn bạn {ho_ten}! Ban tư vấn Tuyển sinh Trường Đại học Kinh tế (DUE) đã tiếp nhận thông tin và sẽ liên hệ hỗ trợ bạn sớm nhất.',
                'data': {
                    'id': yeu_cau.id,
                    'ho_ten': yeu_cau.ho_ten,
                    'ngay_gui': yeu_cau.ngay_gui.strftime('%d/%m/%Y %H:%M')
                }
            })

        messages.success(request, f'Đăng ký tư vấn thành công! Ban tư vấn DUE sẽ liên hệ bạn {ho_ten} trong thời gian sớm nhất.')
        return redirect('admissions:home')

    return redirect('admissions:home')


def news_detail_view(request, slug):
    """Trang chi tiết bài viết tuyển sinh / sự kiện."""
    bai_viet = get_object_or_404(TinTuc, slug=slug)
    bai_viet.luot_xem += 1
    bai_viet.save(update_fields=['luot_xem'])

    tin_lien_quan = TinTuc.objects.exclude(id=bai_viet.id)[:3]
    return render(request, 'admissions/news_detail.html', {
        'bai_viet': bai_viet,
        'tin_lien_quan': tin_lien_quan
    })


def api_search_majors(request):
    """API Tra cứu thông tin ngành học, chỉ tiêu, tổ hợp môn và điểm chuẩn."""
    query = request.GET.get('q', '').strip()
    loai_hinh_param = request.GET.get('loai_hinh', '').strip()
    to_hop_param = request.GET.get('to_hop', '').strip().upper()
    khoa_param = request.GET.get('khoa', '').strip()

    try:
        diem_min = float(request.GET.get('diem_min', 0))
    except (ValueError, TypeError):
        diem_min = 0

    try:
        diem_max = float(request.GET.get('diem_max', 35))
    except (ValueError, TypeError):
        diem_max = 35

    nganh_qs = NganhDaoTao.objects.select_related('loai_hinh').prefetch_related('diem_chuan_cac_nam').all()

    if query:
        nganh_qs = nganh_qs.filter(
            Q(ten_nganh__icontains=query) |
            Q(ma_nganh__icontains=query) |
            Q(to_hop_mon__icontains=query) |
            Q(khoa__icontains=query) |
            Q(mo_ta__icontains=query)
        )

    if loai_hinh_param:
        nganh_qs = nganh_qs.filter(loai_hinh__ma_loai_hinh=loai_hinh_param)

    if to_hop_param:
        nganh_qs = nganh_qs.filter(to_hop_mon__icontains=to_hop_param)

    if khoa_param:
        nganh_qs = nganh_qs.filter(khoa__icontains=khoa_param)

    results = []
    for n in nganh_qs:
        dc_qs = n.diem_chuan_cac_nam.all().order_by('-nam')
        diem_2025 = dc_qs.filter(nam=2025, phuong_thuc='THPT').first()
        diem_2024 = dc_qs.filter(nam=2024, phuong_thuc='THPT').first()
        diem_2023 = dc_qs.filter(nam=2023, phuong_thuc='THPT').first()
        diem_dgnl = dc_qs.filter(nam=2025, phuong_thuc='DGNL').first()

        thpt_score = float(diem_2025.diem_trung_tuyen) if diem_2025 else 0.0

        if diem_min > 0 and thpt_score > 0 and thpt_score < diem_min:
            continue
        if diem_max < 30 and thpt_score > 0 and thpt_score > diem_max:
            continue

        results.append({
            'ma_nganh': n.ma_nganh,
            'ten_nganh': n.ten_nganh,
            'khoa': n.khoa,
            'loai_hinh': n.loai_hinh.ten_loai_hinh if n.loai_hinh else 'Tiêu chuẩn',
            'chi_tieu': n.chi_tieu,
            'chi_tieu_toan_phan': n.chi_tieu_toan_phan,
            'chi_tieu_ban_phan': n.chi_tieu_ban_phan,
            'chi_tieu_tieu_chuan': n.chi_tieu_tieu_chuan,
            'to_hop_mon': n.to_hop_mon,
            'diem_thpt_2025': thpt_score if thpt_score > 0 else None,
            'diem_thpt_2024': float(diem_2024.diem_trung_tuyen) if diem_2024 else None,
            'diem_thpt_2023': float(diem_2023.diem_trung_tuyen) if diem_2023 else None,
            'diem_dgnl_2025': float(diem_dgnl.diem_trung_tuyen) if diem_dgnl else None,
            'hoc_phi_du_kien': n.hoc_phi_du_kien,
            'mo_ta': n.mo_ta,
        })

    return JsonResponse({
        'status': 'success',
        'count': len(results),
        'results': results[:50]
    })


@csrf_exempt
def api_chatbot_legacy(request):
    """API Trợ lý AI Tuyển sinh DUE dựa trên bảng CauHoiThuongGap (hỗ trợ legacy fallback)."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cau_hoi = data.get('question', '').strip()
        except Exception:
            cau_hoi = request.POST.get('question', '').strip()
    else:
        cau_hoi = request.GET.get('q', '').strip()

    if not cau_hoi:
        return JsonResponse({
            'status': 'error',
            'message': 'Vui lòng cung cấp nội dung câu hỏi!'
        }, status=400)

    words = [w.lower() for w in re.split(r'[\s,\.?!;]+', cau_hoi) if len(w) > 1]
    
    exact_matches = CauHoiThuongGap.objects.filter(kich_hoat=True).filter(
        Q(cau_hoi_mau__icontains=cau_hoi) |
        Q(tu_khoa__icontains=cau_hoi) |
        Q(chu_de__icontains=cau_hoi)
    )
    if exact_matches.exists():
        match = exact_matches.first()
        return JsonResponse({
            'status': 'success',
            'found': True,
            'cau_hoi': cau_hoi,
            'chu_de': match.chu_de,
            'phan_loai': match.get_phan_loai_display(),
            'cau_tra_loi': match.cau_tra_loi,
            'nguon_tham_khao': match.nguon_tham_khao or 'https://due.udn.vn',
        })

    candidates = CauHoiThuongGap.objects.filter(kich_hoat=True)
    best_candidate = None
    best_score = 0

    for item in candidates:
        score = 0
        text_corpus = f"{item.chu_de} {item.cau_hoi_mau} {item.tu_khoa} {item.cau_tra_loi}".lower()
        for w in words:
            if w in item.tu_khoa.lower():
                score += 5
            elif w in item.chu_de.lower():
                score += 3
            elif w in item.cau_hoi_mau.lower():
                score += 2
            elif w in text_corpus:
                score += 1
        if score > best_score:
            best_score = score
            best_candidate = item

    if best_candidate and best_score >= 3:
        return JsonResponse({
            'status': 'success',
            'found': True,
            'cau_hoi': cau_hoi,
            'chu_de': best_candidate.chu_de,
            'phan_loai': best_candidate.get_phan_loai_display(),
            'cau_tra_loi': best_candidate.cau_tra_loi,
            'nguon_tham_khao': best_candidate.nguon_tham_khao or 'https://due.udn.vn',
        })

    return JsonResponse({
        'status': 'success',
        'found': False,
        'cau_hoi': cau_hoi,
        'cau_tra_loi': 'Cảm ơn bạn đã đặt câu hỏi! Trợ lý AI DUE đã ghi nhận thắc mắc. Để được tư vấn chi tiết theo hồ sơ và nguyện vọng riêng của bạn, vui lòng liên hệ Ban tuyển sinh DUE qua Hotline: 0236 3836 169 - 0236 3847 139 hoặc gửi form yêu cầu tư vấn trên website nhé!',
        'nguon_tham_khao': 'https://due.udn.vn',
    })


HOLLAND_MAJORS = {
    'E': [
        {'ten': 'Quản trị kinh doanh', 'khoa': 'Khoa Quản trị kinh doanh', 'ma': '7340101', 'diem': '24.50', 'icon': 'corporate_fare'},
        {'ten': 'Marketing', 'khoa': 'Khoa Marketing', 'ma': '7340115', 'diem': '25.50', 'icon': 'campaign'},
        {'ten': 'Kinh doanh quốc tế', 'khoa': 'Khoa Du lịch và KDQT', 'ma': '7340120', 'diem': '25.75', 'icon': 'public'},
        {'ten': 'Kinh doanh thương mại', 'khoa': 'Khoa TMĐT', 'ma': '7340121', 'diem': '24.25', 'icon': 'storefront'},
        {'ten': 'Bất động sản', 'khoa': 'Khoa Tài chính - Ngân hàng', 'ma': '7340116', 'diem': '22.00', 'icon': 'real_estate_agent'},
    ],
    'C': [
        {'ten': 'Kế toán doanh nghiệp', 'khoa': 'Khoa Kế toán', 'ma': '7340301', 'diem': '24.25', 'icon': 'calculate'},
        {'ten': 'Kiểm toán (Chuẩn ACCA)', 'khoa': 'Khoa Kế toán', 'ma': '7340302', 'diem': '25.00', 'icon': 'verified_user'},
        {'ten': 'Tài chính - Ngân hàng', 'khoa': 'Khoa Tài chính - Ngân hàng', 'ma': '7340201', 'diem': '24.00', 'icon': 'account_balance'},
        {'ten': 'Công nghệ Tài chính (Fintech)', 'khoa': 'Khoa Tài chính - Ngân hàng', 'ma': '7340205', 'diem': '24.75', 'icon': 'currency_exchange'},
        {'ten': 'Luật Kinh tế', 'khoa': 'Khoa Luật', 'ma': '7380107', 'diem': '24.50', 'icon': 'gavel'},
    ],
    'I': [
        {'ten': 'Khoa học dữ liệu trong Kinh tế', 'khoa': 'Khoa Thống kê - Tin học', 'ma': '7310108', 'diem': '24.50', 'icon': 'query_stats'},
        {'ten': 'Thương mại điện tử', 'khoa': 'Khoa TMĐT', 'ma': '7340122', 'diem': '25.25', 'icon': 'shopping_cart'},
        {'ten': 'Hệ thống thông tin quản lý', 'khoa': 'Khoa TMĐT', 'ma': '7340405', 'diem': '24.00', 'icon': 'lan'},
        {'ten': 'Kinh tế đầu tư và phát triển', 'khoa': 'Khoa Kinh tế', 'ma': '7310101', 'diem': '23.00', 'icon': 'trending_up'},
        {'ten': 'Thống kê kinh tế', 'khoa': 'Khoa Thống kê - Tin học', 'ma': '7460117', 'diem': '22.50', 'icon': 'bar_chart'},
    ],
    'S': [
        {'ten': 'Quản trị khách sạn', 'khoa': 'Khoa Du lịch và KDQT', 'ma': '7810201', 'diem': '24.00', 'icon': 'hotel'},
        {'ten': 'Quản trị dịch vụ du lịch và lữ hành', 'khoa': 'Khoa Du lịch và KDQT', 'ma': '7810103', 'diem': '23.50', 'icon': 'travel_explore'},
        {'ten': 'Quản trị nhân lực', 'khoa': 'Khoa Quản trị kinh doanh', 'ma': '7340101_02', 'diem': '24.50', 'icon': 'diversity_3'},
        {'ten': 'Luật học', 'khoa': 'Khoa Luật', 'ma': '7380101', 'diem': '23.50', 'icon': 'balance'},
    ],
    'A': [
        {'ten': 'Truyền thông Marketing tích hợp (IMC)', 'khoa': 'Khoa Marketing', 'ma': '7340115_02', 'diem': '25.50', 'icon': 'podcasts'},
        {'ten': 'Marketing Số (Digital Marketing)', 'khoa': 'Khoa Marketing', 'ma': '7340115_01', 'diem': '25.75', 'icon': 'ads_click'},
        {'ten': 'Cử nhân Quốc tế (Liên kết Anh/Úc)', 'khoa': 'Viện Đào tạo Quốc tế', 'ma': '7340101_QT', 'diem': '22.00', 'icon': 'language'},
    ],
    'R': [
        {'ten': 'Quản trị chuỗi cung ứng và logistics', 'khoa': 'Khoa Quản trị kinh doanh', 'ma': '7340101_03', 'diem': '25.50', 'icon': 'local_shipping'},
        {'ten': 'Hệ thống thông tin quản lý', 'khoa': 'Khoa TMĐT', 'ma': '7340405', 'diem': '24.00', 'icon': 'dns'},
        {'ten': 'Công nghệ Tài chính (Fintech)', 'khoa': 'Khoa Tài chính - Ngân hàng', 'ma': '7340205', 'diem': '24.75', 'icon': 'payments'},
    ]
}


@csrf_exempt
@rate_limit(key_prefix='advisory', max_requests=5, timeout_seconds=60)
def api_career_advisory(request):
    """API Tiếp nhận trắc nghiệm Holland và phân tích hướng nghiệp."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Chỉ chấp nhận phương thức POST'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    ho_ten = data.get('full_name', '').strip()
    so_dien_thoai = data.get('phone_number', '').strip()
    email = data.get('email', '').strip()

    if not ho_ten or not so_dien_thoai:
        return JsonResponse({
            'status': 'error',
            'message': 'Vui lòng cung cấp đầy đủ Họ tên và Số điện thoại!'
        }, status=400)

    scores = {
        'R': int(data.get('score_r', 0)),
        'I': int(data.get('score_i', 0)),
        'A': int(data.get('score_a', 0)),
        'S': int(data.get('score_s', 0)),
        'E': int(data.get('score_e', 0)),
        'C': int(data.get('score_c', 0)),
    }

    sorted_letters = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
    holland_code = "".join(sorted_letters[:3]) if any(scores.values()) else ""

    EXTRA_FIELDS = [
        ('grade_level', 'Đang học lớp'),
        ('subject_combo', 'Tổ hợp môn dự định xét tuyển'),
        ('expected_score', 'Điểm thi/điểm xét tuyển dự kiến (thang 30)'),
        ('gpa', 'Điểm trung bình học tập'),
        ('strong_subjects', 'Môn học giỏi nhất'),
        ('weak_subjects', 'Môn học yếu nhất'),
        ('english_level', 'Trình độ tiếng Anh / chứng chỉ'),
        ('admission_method', 'Phương thức xét tuyển dự định'),
        ('program_type', 'Chương trình mong muốn'),
        ('budget', 'Khả năng chi trả học phí/năm'),
        ('work_style', 'Môi trường làm việc mong muốn'),
        ('job_priority', 'Ưu tiên khi chọn nghề'),
        ('considered_majors', 'Ngành đang cân nhắc'),
        ('family_wish', 'Mong muốn của gia đình'),
        ('extra_notes', 'Ghi chú thêm'),
    ]
    extra = {label: str(data.get(key, '')).strip() for key, label in EXTRA_FIELDS}
    extra = {k: v for k, v in extra.items() if v}

    profile = {
        'Giới tính': data.get('gender', ''),
        'Tỉnh/Thành': data.get('province', ''),
        'Sở thích': data.get('interests', ''),
        'Năng lực, điểm mạnh': data.get('strengths', ''),
        'Định hướng nghề nghiệp': data.get('career_goals', ''),
        **extra,
    }

    ai_result = None
    ai_error = ''
    try:
        from . import ai_advisor
        ai_result = ai_advisor.analyze(profile, scores, holland_code)
    except Exception as e:
        ai_error = str(e)

    suggested = []
    seen = set()
    for letter in sorted_letters[:3]:
        for major in HOLLAND_MAJORS.get(letter, []):
            if major['ten'] not in seen:
                seen.add(major['ten'])
                suggested.append(major)
            if len(suggested) >= 6:
                break
        if len(suggested) >= 6:
            break

    if ai_result:
        suggested = ai_result['majors']
        nganh_txt = "\n".join(
            f"{i+1}. {m['ten']} ({m['ma']}) - {m['phu_hop']}%: {m['ly_do']}" for i, m in enumerate(suggested)
        )
        nganh_txt = f"[AI] {ai_result['tong_quan']}\n{nganh_txt}\nLời khuyên: {ai_result['loi_khuyen']}"
    else:
        nganh_txt = ", ".join([s['ten'] for s in suggested])

    so_truong = data.get('strengths', '')
    if extra:
        so_truong += "\n\n--- THÔNG TIN BỔ SUNG ---\n" + "\n".join(f"{k}: {v}" for k, v in extra.items())

    hoso = HoSoHuongNghiep.objects.create(
        ho_ten=ho_ten,
        gioi_tinh=data.get('gender', 'Nam'),
        ngay_sinh=data.get('date_of_birth', ''),
        so_dien_thoai=so_dien_thoai,
        email=email,
        truong_thpt=data.get('high_school', ''),
        tinh_thanh=data.get('province', ''),
        dia_chi=data.get('address', ''),
        so_thich=data.get('interests', ''),
        so_truong=so_truong,
        muc_tieu_nghe_nghiep=data.get('career_goals', ''),
        diem_r=scores['R'],
        diem_i=scores['I'],
        diem_a=scores['A'],
        diem_s=scores['S'],
        diem_e=scores['E'],
        diem_c=scores['C'],
        ma_holland=holland_code,
        nganh_de_xuat=nganh_txt,
    )

    return JsonResponse({
        'status': 'success',
        'message': f'Hồ sơ của bạn {ho_ten} đã được lưu thành công vào Cổng thông tin Tuyển sinh DUE.',
        'data': {
            'id': hoso.id,
            'holland_code': holland_code,
            'scores': scores,
            'suggested_majors': suggested,
            'ai': bool(ai_result),
            'ai_error': ai_error,
            'tong_quan': ai_result['tong_quan'] if ai_result else '',
            'loi_khuyen': ai_result['loi_khuyen'] if ai_result else '',
        }
    })


def api_statistics(request):
    """API cung cấp các số liệu thống kê tuyển sinh DUE."""
    return JsonResponse({
        'status': 'success',
        'ma_truong': 'DDQ',
        'tong_chi_tieu_2026': 4600,
        'ty_le_viec_lam': '98.5%',
        'quy_hoc_bong': '15 Tỷ',
        'so_nganh_dao_tao': NganhDaoTao.objects.count(),
        'so_phuong_thuc': PhuongThucXetTuyen.objects.count(),
        'so_loai_hinh': LoaiHinhDaoTao.objects.count(),
    })


def tuition_fees_view(request):
    """Trang Học phí và lộ trình 4 năm."""
    tuition_list = BangHocPhi.objects.filter(is_active=True).order_by('order')
    faq_list = CauHoiHocPhi.objects.filter(is_active=True).order_by('order')

    tuition_rates = {}
    for t in tuition_list:
        slug = t.slug or f"nhom-{t.id}"
        tuition_rates[slug] = [
            float(t.nam_hoc_1),
            float(t.nam_hoc_2),
            float(t.nam_hoc_3),
            float(t.nam_hoc_4)
        ]
    tuition_rates_json = json.dumps(tuition_rates, ensure_ascii=False)

    context = {
        'tuition_list': tuition_list,
        'faq_list': faq_list,
        'tuition_rates_json': tuition_rates_json,
    }
    return render(request, 'admissions/tuition_fees.html', context)


def api_calculate_tuition(request):
    """API tính toán học phí theo chương trình và năm học."""
    slug = (request.GET.get('slug') or request.GET.get('program') or 'tieu-chuan').strip().lower()
    
    slug_map = {
        'tiêu-chuẩn': 'tieu-chuan',
        'tài-năng': 'tai-nang',
        'toàn-phần-ta': 'toan-phan-ta',
        'bán-phần-ta': 'ban-phan-ta',
    }
    target_slug = slug_map.get(slug, slug)
    
    try:
        year_index = int(request.GET.get('year', 0))
    except (ValueError, TypeError):
        year_index = 0

    tuition = BangHocPhi.objects.filter(is_active=True).filter(
        Q(slug=target_slug) | Q(slug=slug)
    ).first()

    if not tuition:
        tuition = BangHocPhi.objects.filter(is_active=True).first()

    if tuition:
        rates = [tuition.nam_hoc_1, tuition.nam_hoc_2, tuition.nam_hoc_3, tuition.nam_hoc_4]
        if 0 <= year_index < len(rates):
            mil = float(rates[year_index])
            year_vnd = int(mil * 1_000_000)
            term_vnd = int(year_vnd / 2)
            return JsonResponse({
                'status': 'success',
                'program': tuition.nhom,
                'year_vnd': year_vnd,
                'term_vnd': term_vnd,
                'year_vnd_formatted': f"{year_vnd:,.0f}".replace(",", "."),
                'term_vnd_formatted': f"{term_vnd:,.0f}".replace(",", ".")
            })

    return JsonResponse({'status': 'error', 'message': 'Không tìm thấy thông tin chương trình'}, status=400)


def format_file_size(size_bytes):
    if size_bytes == 0:
        return '0 B'
    size_name = ('B', 'KB', 'MB', 'GB')
    i = 0
    p = 1024
    s = size_bytes
    while s >= p and i < len(size_name) - 1:
        s /= p
        i += 1
    return f"{s:.1f} {size_name[i]}"


def _staff_required_json(request):
    """Trả về JsonResponse lỗi nếu không phải cán bộ (staff), ngược lại None."""
    if not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse({'status': 'error', 'message': 'Chỉ cán bộ tuyển sinh đã đăng nhập mới được thực hiện.'}, status=403)
    return None


def api_documents_list(request):
    """API trả về danh sách các tài liệu đã upload."""
    docs = TaiLieuTuyenSinh.objects.all().order_by('-uploaded_at')
    data = []
    for d in docs:
        data.append({
            'id': d.id,
            'name': d.title,
            'size': d.file_size,
            'url': d.file.url if d.file else '',
            'date': d.uploaded_at.strftime('%H:%M - %d/%m/%Y'),
            'is_processed': d.is_processed,
        })
    return JsonResponse({'status': 'success', 'data': data})


def api_documents_upload(request):
    """API tiếp nhận upload tài liệu từ Cán bộ tư vấn (chỉ staff)."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Chỉ hỗ trợ phương thức POST'}, status=405)
    denied = _staff_required_json(request)
    if denied:
        return denied

    files = request.FILES.getlist('files')
    if not files:
        return JsonResponse({'status': 'error', 'message': 'Không có tệp nào được gửi lên'}, status=400)

    saved_items = []
    for f in files:
        doc = TaiLieuTuyenSinh(title=f.name, file=f, file_size=format_file_size(f.size))
        doc.save()
        error = ''
        try:
            n = rag.index_document(doc)
        except Exception as e:
            n, error = 0, str(e)
        saved_items.append({
            'id': doc.id,
            'name': doc.title,
            'size': doc.file_size,
            'url': doc.file.url,
            'date': doc.uploaded_at.strftime('%H:%M - %d/%m/%Y'),
            'is_processed': doc.is_processed,
            'chunks': n,
            'error': error,
        })

    return JsonResponse({
        'status': 'success',
        'message': f'Đã tải lên {len(saved_items)} tài liệu',
        'data': saved_items
    })


def api_documents_delete(request, doc_id):
    """API xóa tài liệu (chỉ staff)."""
    if request.method not in ['POST', 'DELETE']:
        return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ'}, status=405)
    denied = _staff_required_json(request)
    if denied:
        return denied

    try:
        doc = TaiLieuTuyenSinh.objects.get(id=doc_id)
        if doc.file:
            doc.file.delete(save=False)
        doc.delete()
        return JsonResponse({'status': 'success', 'message': 'Đã xóa tài liệu'})
    except TaiLieuTuyenSinh.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Tài liệu không tồn tại'}, status=404)


HANDOFF_REPLY = (
    'Câu hỏi này hiện chưa có trong tài liệu của Chatbot nên đã được **chuyển tới cán bộ tuyển sinh DUE**. '
    'Bạn vui lòng giữ trang này, câu trả lời sẽ hiện ngay trong khung chat khi cán bộ phản hồi. '
    'Cần gấp, bạn có thể gọi Hotline 0236 3836 169.'
)


def _clean_client_id(value):
    value = str(value or '')
    return value if re.fullmatch(r'[A-Za-z0-9_-]{8,64}', value) else ''


@csrf_exempt
@rate_limit(key_prefix='chat', max_requests=15, timeout_seconds=60)
def api_chat(request):
    """API tiếp nhận chat hội thoại và trả lời theo RAG."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Chỉ hỗ trợ POST'}, status=405)
    try:
        body = json.loads(request.body.decode('utf-8'))
        question = (body.get('message') or '').strip()[:2000]
        history = body.get('history') or []
        client_id = _clean_client_id(body.get('client_id'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'JSON không hợp lệ'}, status=400)
    if not question:
        return JsonResponse({'status': 'error', 'message': 'Câu hỏi trống'}, status=400)
    if not client_id:
        return JsonResponse({'status': 'error', 'message': 'Thiếu mã phiên chat'}, status=400)

    try:
        reply, sources, found = rag.answer(question, history)
    except Exception as e:
        reply, sources, found = '', [], False
        print('chat_api AI error:', e)

    if found:
        return JsonResponse({'status': 'success', 'reply': reply, 'sources': sources, 'handoff': False})

    ngu_canh = "\n".join(f"{m.get('role')}: {m.get('content')}" for m in history[-6:] if isinstance(m, dict))
    q = CauHoiChoTraLoi.objects.create(client_id=client_id, cau_hoi=question, ngu_canh=ngu_canh[:4000])
    return JsonResponse({'status': 'success', 'reply': HANDOFF_REPLY, 'sources': [],
                         'handoff': True, 'pending_id': q.id})


def api_chat_updates(request):
    """Người hỏi lấy các câu trả lời của cán bộ cho phiên chat của mình (polling)."""
    client_id = _clean_client_id(request.GET.get('client_id'))
    if not client_id:
        return JsonResponse({'status': 'error', 'message': 'Thiếu mã phiên chat'}, status=400)
    items = CauHoiChoTraLoi.objects.filter(client_id=client_id).order_by('ngay_tao')
    return JsonResponse({'status': 'success', 'data': [{
        'id': q.id,
        'cau_hoi': q.cau_hoi,
        'trang_thai': q.trang_thai,
        'tra_loi': q.tra_loi if q.trang_thai == 'da_tra_loi' else '',
    } for q in items]})


def officer_qa_view(request):
    """Trang giao diện dành cho cán bộ tuyển sinh trả lời câu hỏi Chatbot."""
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect(f'/admin/login/?next={request.path}')
    return render(request, 'admissions/officer_qa.html')


def api_officer_questions(request):
    """API lấy danh sách câu hỏi đang chờ cán bộ trả lời."""
    denied = _staff_required_json(request)
    if denied:
        return denied
    trang_thai = request.GET.get('trang_thai', 'cho')
    qs = CauHoiChoTraLoi.objects.select_related('can_bo')
    if trang_thai in ('cho', 'da_tra_loi'):
        qs = qs.filter(trang_thai=trang_thai)
    qs = qs.order_by('ngay_tao' if trang_thai == 'cho' else '-ngay_tra_loi')[:200]
    return JsonResponse({
        'status': 'success',
        'pending_count': CauHoiChoTraLoi.objects.filter(trang_thai='cho').count(),
        'data': [{
            'id': q.id,
            'cau_hoi': q.cau_hoi,
            'ngu_canh': q.ngu_canh,
            'tra_loi': q.tra_loi,
            'trang_thai': q.trang_thai,
            'can_bo': (q.can_bo.get_full_name() or q.can_bo.username) if q.can_bo else '',
            'da_them_kien_thuc': q.da_them_kien_thuc,
            'ngay_tao': timezone.localtime(q.ngay_tao).strftime('%H:%M %d/%m/%Y'),
            'ngay_tra_loi': timezone.localtime(q.ngay_tra_loi).strftime('%H:%M %d/%m/%Y') if q.ngay_tra_loi else '',
        } for q in qs],
    })


def api_officer_reply(request, q_id):
    """API cán bộ trả lời câu hỏi và tùy chọn đưa vào kho tri thức RAG."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Chỉ hỗ trợ POST'}, status=405)
    denied = _staff_required_json(request)
    if denied:
        return denied
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'JSON không hợp lệ'}, status=400)
    tra_loi = (body.get('tra_loi') or '').strip()
    if not tra_loi:
        return JsonResponse({'status': 'error', 'message': 'Câu trả lời trống'}, status=400)

    q = get_object_or_404(CauHoiChoTraLoi, id=q_id)
    q.tra_loi = tra_loi
    q.trang_thai = 'da_tra_loi'
    q.can_bo = request.user
    q.ngay_tra_loi = timezone.now()

    msg = 'Đã gửi câu trả lời'
    if body.get('them_kien_thuc') and not q.da_them_kien_thuc:
        try:
            rag.add_knowledge(q.cau_hoi, tra_loi)
            q.da_them_kien_thuc = True
            msg += ' và thêm vào kho kiến thức của Chatbot'
        except Exception as e:
            msg += f' (chưa thêm được vào kho kiến thức: {e})'
    q.save()
    return JsonResponse({'status': 'success', 'message': msg})


def chatbot_view(request):
    """Trang giao diện Chatbot Tuyển sinh toàn màn hình."""
    return render(request, 'admissions/chatbot.html')


def career_advisory_view(request):
    """Trang Tư vấn chọn ngành và trắc nghiệm nghề nghiệp Holland."""
    return render(request, 'admissions/career_advisory.html')
