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
