import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.db.models import Q, Sum
from .models import (
    TinTuc,
    LoaiHinhDaoTao,
    NganhDaoTao,
    DiemChuan,
    PhuongThucXetTuyen,
    CauHoiThuongGap,
    TuVanTuyenSinh
)


def home(request):
    """
    Trang chủ Cổng thông tin Tuyển sinh DUE
    Cung cấp dữ liệu động từ Database cho tin tức, ngành đào tạo, phương thức và thống kê.
    """
    tin_tuc_list = TinTuc.objects.filter(noi_bat=True)[:6]
    nganh_list = NganhDaoTao.objects.all()[:8]
    loai_hinh_list = LoaiHinhDaoTao.objects.all().order_by('thu_tu')
    phuong_thuc_list = PhuongThucXetTuyen.objects.all().order_by('thu_tu')
    
    # Thống kê tổng quan
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
    return render(request, 'home.html', context)

home_view = home



def lich_su_phat_trien(request):
    """
    Trang Lịch sử phát triển DUE (Chuyến tàu 50 năm)
    """
    return render(request, 'lichsuphattrien.html')


def su_mang_tam_nhin(request):
    """
    Trang Sứ mạng & Tầm nhìn DUE
    """
    return render(request, 'sumangtamnhin.html')


def phuong_thuc_xet_tuyen(request):
    """
    Trang Phương thức xét tuyển đại học chính quy năm 2026 - DUE
    """
    phuong_thuc_list = PhuongThucXetTuyen.objects.all().order_by('thu_tu')
    context = {
        'phuong_thuc_list': phuong_thuc_list,
    }
    return render(request, 'phuongthucxettuyen.html', context)


def diem_chuan_cac_nam(request):
    """
    Trang Tra cứu Điểm chuẩn các năm (2022 - 2025) - DUE
    """
    diem_chuan_list = DiemChuan.objects.select_related('nganh').all().order_by('-nam', 'nganh__ma_nganh')
    nam_list = DiemChuan.objects.values_list('nam', flat=True).distinct().order_by('-nam')
    
    context = {
        'diem_chuan_list': diem_chuan_list,
        'nam_list': nam_list,
    }
    return render(request, 'diemchuancacnam.html', context)


def chi_tieu_tuyen_sinh(request):
    """
    Trang Chỉ tiêu tuyển sinh đại học năm 2026 - DUE
    """
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
    return render(request, 'chitieutuyensinh.html', context)


def loai_hinh_dao_tao(request):
    """
    Trang 3 Loại hình đào tạo đại học chính quy năm 2026 - DUE
    (Toàn phần tiếng Anh, Bán phần tiếng Anh, Tiêu chuẩn)
    """
    loai_hinh_list = LoaiHinhDaoTao.objects.prefetch_related('nganh_hoc').all().order_by('thu_tu')
    context = {
        'loai_hinh_list': loai_hinh_list,
    }
    return render(request, 'loaihinhdaotao.html', context)


def dang_nhap(request):
    """
    Xử lý Đăng nhập Cổng thông tin Tuyển sinh DUE
    Hỗ trợ cả Modal Popup (AJAX JSON) và Form truyền thống
    """
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
        return redirect('tuyensinh:home')

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
                    request.session.set_expiry(0)  # Hết hạn khi đóng trình duyệt
                else:
                    request.session.set_expiry(1209600)  # 2 tuần

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
                return redirect('tuyensinh:home')
            else:
                msg = "Tên đăng nhập hoặc mật khẩu không chính xác. Vui lòng kiểm tra lại!"
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': msg}, status=400)
                error_message = msg

    return render(request, 'login.html', {'error_message': error_message})


def dang_xuat(request):
    """
    Đăng xuất khỏi hệ thống
    """
    auth_logout(request)
    messages.info(request, "Bạn đã đăng xuất khỏi Cổng thông tin Tuyển sinh DUE.")
    return redirect('tuyensinh:home')


def dang_ky_tu_van(request):
    """
    API & Form tiếp nhận đăng ký tư vấn tuyển sinh từ thí sinh/phụ huynh
    Hỗ trợ xử lý cả AJAX (JSON) và gửi Form truyền thống.
    """
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
            return redirect('tuyensinh:home')

        # Lưu yêu cầu vào cơ sở dữ liệu
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
        return redirect('tuyensinh:home')

    return redirect('tuyensinh:home')


def chi_tiet_tin_tuc(request, slug):
    """
    Trang chi tiết bài viết tuyển sinh / sự kiện
    """
    bai_viet = get_object_or_404(TinTuc, slug=slug)
    # Tăng lượt xem
    bai_viet.luot_xem += 1
    bai_viet.save(update_fields=['luot_xem'])

    tin_lien_quan = TinTuc.objects.exclude(id=bai_viet.id)[:3]
    return render(request, 'chi_tiet_tin_tuc.html', {
        'bai_viet': bai_viet,
        'tin_lien_quan': tin_lien_quan
    })


# ========================================================
# CÁC API ENDPOINTS PHỤC VỤ TÌM KIẾM & CHATBOT THÔNG MINH
# ========================================================

def api_tra_cuu_nganh(request):
    """
    API Tra cứu thông tin ngành học, chỉ tiêu, tổ hợp môn và điểm chuẩn
    GET /api/tra-cuu/?q=Marketing&loai_hinh=toan_phan
    """
    query = request.GET.get('q', '').strip()
    loai_hinh_param = request.GET.get('loai_hinh', '').strip()

    nganh_qs = NganhDaoTao.objects.select_related('loai_hinh').all()

    if query:
        nganh_qs = nganh_qs.filter(
            Q(ten_nganh__icontains=query) |
            Q(ma_nganh__icontains=query) |
            Q(to_hop_mon__icontains=query) |
            Q(khoa__icontains=query)
        )

    if loai_hinh_param:
        nganh_qs = nganh_qs.filter(loai_hinh__ma_loai_hinh=loai_hinh_param)

    results = []
    for n in nganh_qs[:30]:
        diem_2025 = n.diem_chuan_cac_nam.filter(nam=2025, phuong_thuc='THPT').first()
        diem_dgnl = n.diem_chuan_cac_nam.filter(nam=2025, phuong_thuc='DGNL').first()

        results.append({
            'ma_nganh': n.ma_nganh,
            'ten_nganh': n.ten_nganh,
            'loai_hinh': n.loai_hinh.ten_loai_hinh if n.loai_hinh else 'Tiêu chuẩn',
            'chi_tieu': n.chi_tieu,
            'to_hop_mon': n.to_hop_mon,
            'diem_thpt_2025': float(diem_2025.diem_trung_tuyen) if diem_2025 else None,
            'diem_dgnl_2025': float(diem_dgnl.diem_trung_tuyen) if diem_dgnl else None,
            'mo_ta': n.mo_ta,
        })

    return JsonResponse({
        'status': 'success',
        'count': len(results),
        'results': results
    })


def api_chatbot(request):
    """
    API Trợ lý AI Tuyển sinh DUE (Hỏi đáp tự động từ cơ sở tri thức CauHoiThuongGap)
    POST /api/chatbot/ hoặc GET /api/chatbot/?q=...
    """
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            cau_hoi = data.get('question', '').strip()
        except:
            cau_hoi = request.POST.get('question', '').strip()
    else:
        cau_hoi = request.GET.get('q', '').strip()

    if not cau_hoi:
        return JsonResponse({
            'status': 'error',
            'message': 'Vui lòng cung cấp nội dung câu hỏi!'
        }, status=400)

    words = [w.lower() for w in cau_hoi.split() if len(w) > 1]
    q_filter = Q()
    for w in words:
        q_filter |= Q(cau_hoi_mau__icontains=w) | Q(tu_khoa__icontains=w) | Q(chu_de__icontains=w) | Q(cau_tra_loi__icontains=w)

    cau_tra_loi_match = CauHoiThuongGap.objects.filter(kich_hoat=True).filter(q_filter).first()

    if cau_tra_loi_match:
        return JsonResponse({
            'status': 'success',
            'found': True,
            'cau_hoi': cau_hoi,
            'chu_de': cau_tra_loi_match.chu_de,
            'phan_loai': cau_tra_loi_match.get_phan_loai_display(),
            'cau_tra_loi': cau_tra_loi_match.cau_tra_loi,
            'nguon_tham_khao': cau_tra_loi_match.nguon_tham_khao or 'https://due.udn.vn',
        })
    else:
        return JsonResponse({
            'status': 'success',
            'found': False,
            'cau_hoi': cau_hoi,
            'cau_tra_loi': 'Xin lỗi, câu hỏi của bạn chưa có sẵn trong cơ sở dữ liệu tự động. Bạn vui lòng liên hệ trực tiếp Hotline Tư vấn Tuyển sinh DUE: 0236 3836 169 hoặc gửi form yêu cầu tư vấn để được hỗ trợ chi tiết nhất nhé!',
            'nguon_tham_khao': 'https://due.udn.vn',
        })


def api_thong_ke(request):
    """
    API cung cấp các số liệu thống kê tuyển sinh DUE
    """
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


# ========================================================
# VIEWS CHO KHOA & HỌC PHÍ (TỪ NHÁNH MAIN)
# ========================================================

from .models import KhoaPhongBan, BangHocPhi, CauHoiHocPhi, ChinhSachHocBong

def khoa_view(request):
    """
    Trang danh sách Khoa Đào Tạo & Phòng Ban Chức Năng.
    Lấy dữ liệu động từ Database và cung cấp JSON cho modal tương tác.
    """
    khoa_list = KhoaPhongBan.objects.filter(is_active=True, category='khoa').prefetch_related('majors')
    phongban_list = KhoaPhongBan.objects.filter(is_active=True, category='phong_ban').prefetch_related('majors')

    all_items = KhoaPhongBan.objects.filter(is_active=True).prefetch_related('majors')
    data_khoa_dict = {item.code: item.to_dict() for item in all_items}
    data_khoa_json = json.dumps(data_khoa_dict, ensure_ascii=False)

    context = {
        'khoa_list': khoa_list,
        'phongban_list': phongban_list,
        'data_khoa_json': data_khoa_json,
        'khoa_count': khoa_list.count(),
        'phongban_count': phongban_list.count(),
    }
    return render(request, 'khoa.html', context)

def khoa_detail_api(request, code):
    """API trả về chi tiết thông tin 1 Khoa hoặc Phòng ban dưới dạng JSON"""
    item = get_object_or_404(KhoaPhongBan, code=code, is_active=True)
    return JsonResponse({
        'status': 'success',
        'data': item.to_dict()
    })

def hoc_phi_view(request):
    """
    Trang Học phí & Lộ trình 4 năm.
    Dữ liệu bảng học phí, câu hỏi FAQ và mức tính toán được lấy trực tiếp từ Database.
    """
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
    return render(request, 'hocphi.html', context)

def tinh_hoc_phi_api(request):
    """API tính toán học phí theo chương trình và năm học"""
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

