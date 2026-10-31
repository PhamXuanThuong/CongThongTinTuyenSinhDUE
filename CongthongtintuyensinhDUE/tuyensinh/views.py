import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import KhoaPhongBan, BangHocPhi, CauHoiHocPhi, ChinhSachHocBong

def home_view(request):
    """Trang chủ cổng thông tin tuyển sinh"""
    return render(request, 'home.html')

def khoa_view(request):
    """
    Trang danh sách Khoa Đào Tạo & Phòng Ban Chức Năng.
    Lấy dữ liệu động từ Database và cung cấp JSON cho modal tương tác.
    """
    khoa_list = KhoaPhongBan.objects.filter(is_active=True, category='khoa').prefetch_related('majors')
    phongban_list = KhoaPhongBan.objects.filter(is_active=True, category='phong_ban').prefetch_related('majors')

    # Xây dựng từ điển dữ liệu cho modal popup (Client-side JS)
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

    # Dữ liệu phục vụ công cụ tính học phí tự động trên giao diện
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
