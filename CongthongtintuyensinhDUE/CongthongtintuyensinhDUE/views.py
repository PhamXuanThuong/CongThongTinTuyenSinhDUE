import json
import os
import unicodedata
import re
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
# Re-export views from tuyensinh app
from tuyensinh.views import home_view as home, hoc_phi_view as hoc_phi

FACULTY_NAMES = {
    'tcnh': 'Khoa Tài chính - Ngân hàng',
    'dlkdqt': 'Khoa Du lịch & Kinh doanh quốc tế',
    'tmdt_mkt_cns': 'Khoa Thương mại điện tử - Marketing và Công nghệ số',
    'kt': 'Khoa Kinh tế',
    'qtkd': 'Khoa Quản trị kinh doanh',
    'ketoan': 'Khoa Kế toán',
    'llct': 'Khoa Lý luận chính trị',
    'luat': 'Khoa Luật',
    'vdtqt': 'Viện Đào tạo Quốc tế',
}

def load_faculty_data():
    """Tải danh sách 9 Khoa & Viện đào tạo 2026 kèm đầy đủ thông tin chuyên sâu"""
    khoa_path = os.path.join(settings.BASE_DIR, 'data', 'khoa.json')
    if os.path.exists(khoa_path):
        with open(khoa_path, 'r', encoding='utf-8') as f:
            faculties = json.load(f)
            for fac in faculties:
                fid = fac.get('id')
                fac['logo_url'] = f'/static/img/khoa/{fid}_logo.png'
                fac['cover_url'] = f'/static/img/khoa/{fid}_cover.jpg'
                fac['detail_url'] = f'/khoa/{fid}/'
                fac['lcd_url'] = f'/lien-chi-doan/{fid}/'
                
                # Format gallery
                if 'gallery' in fac and isinstance(fac['gallery'], list):
                    for g in fac['gallery']:
                        if isinstance(g, dict) and 'url' in g:
                            if not g['url'].startswith('/'):
                                g['url'] = f'/static/img/khoa/{os.path.basename(g["url"])}'
                                
                # Format LCD data
                if 'lcd' in fac and isinstance(fac['lcd'], dict):
                    fac['lcd']['detail_url'] = f'/lien-chi-doan/{fid}/'
                    fac['lcd']['faculty_id'] = fid
                    fac['lcd']['faculty_name'] = fac.get('name')
                    fac['lcd']['color'] = fac.get('color', 'bg-blue-600')
                    fac['lcd']['gradient'] = fac.get('gradient', 'from-blue-600 to-indigo-700')
                    if 'images' in fac['lcd'] and isinstance(fac['lcd']['images'], list):
                        for img in fac['lcd']['images']:
                            if isinstance(img, dict) and 'url' in img:
                                if not img['url'].startswith('/'):
                                    img['url'] = f'/static/img/lcd/{os.path.basename(img["url"])}'
            return faculties
    return []

def load_phongban_data():
    """Tải danh sách 9 Phòng ban chức năng & Trung tâm trực thuộc DUE"""
    pb_path = os.path.join(settings.BASE_DIR, 'data', 'phongban.json')
    if os.path.exists(pb_path):
        with open(pb_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def khoa_overview_view(request):
    """
    Trang tổng quan danh sách 9 Khoa chuyên sâu & 9 Phòng ban chức năng DUE (Cơ cấu 2026).
    Mỗi thẻ Khoa liên kết trực tiếp sang trang chi tiết riêng (/khoa/<id>/), không dùng popup.
    """
    faculties = load_faculty_data()
    phongban_list = load_phongban_data()
    
    return render(request, 'khoa.html', {
        'faculties': faculties,
        'phongban_list': phongban_list,
        'faculty_count': len(faculties),
        'phongban_count': len(phongban_list),
    })

def khoa_detail_view(request, code):
    """
    Trang chi tiết chuyên sâu của từng Khoa/Viện đào tạo.
    Chứa đầy đủ: Lịch sử, Sứ mệnh/Tầm nhìn, Thông điệp Trưởng khoa,
    Toàn bộ chuyên ngành 2026, Sau đại học, Đội ngũ & Bộ môn,
    Cơ hội việc làm, Đối tác doanh nghiệp, Đời sống sinh viên & CLB, Thư viện ảnh,
    và khối thông tin đầy đủ các Phòng ban chức năng & Trung tâm ở cuối trang.
    """
    faculties = load_faculty_data()
    clean_code = code.strip().rstrip('/').lower()
    
    # Chuẩn hoá tìm kiếm theo id hoặc alias
    target_faculty = None
    for fac in faculties:
        fid = fac.get('id', '').lower()
        aliases = [a.lower() for a in fac.get('aliases', [])]
        if fid == clean_code or clean_code in aliases:
            target_faculty = fac
            break

    if not target_faculty:
        # Thử tìm kiếm mờ không phân biệt dấu gạch nối hoặc gạch dưới
        norm_code = clean_code.replace('-', '_')
        for fac in faculties:
            if fac.get('id', '').replace('-', '_') == norm_code:
                target_faculty = fac
                break

    if not target_faculty:
        return redirect('khoa')

    # Danh sách các khoa khác phục vụ chuyển nhanh (Quick Switcher)
    other_faculties = [f for f in faculties if f.get('id') != target_faculty.get('id')]
    phongban_list = load_phongban_data()
    
    # Nạp các câu lạc bộ thuộc khoa này (nếu có)
    all_clubs = load_clb_data()
    faculty_clubs = [c for c in all_clubs if c.get('faculty_id') == target_faculty.get('id')]

    return render(request, 'khoa_detail.html', {
        'faculty': target_faculty,
        'other_faculties': other_faculties,
        'all_faculties': faculties,
        'phongban_list': phongban_list,
        'faculty_clubs': faculty_clubs,
    })

def lien_chi_doan_overview_view(request):
    """
    Trang tổng quan Hệ thống Liên Chi Đoàn 9 Khoa & Viện Đào Tạo DUE
    + Đoàn Thanh niên - Hội Sinh viên Trường Đại học Kinh tế DUE.
    """
    faculties = load_faculty_data()
    all_clubs = load_clb_data()
    
    # Map clubs to each faculty LCD
    for fac in faculties:
        fid = fac.get('id')
        fac_clubs = [c for c in all_clubs if c.get('faculty_id') == fid]
        fac['clubs_count'] = len(fac_clubs)
        fac['faculty_clubs'] = fac_clubs
        
    return render(request, 'lien_chi_doan_list.html', {
        'faculties': faculties,
        'faculty_count': len(faculties),
        'clubs_count': len(all_clubs),
    })

def lien_chi_doan_detail_view(request, code):
    """
    Trang chi tiết chuyên sâu riêng biệt của Liên Chi Đoàn từng Khoa.
    Bao gồm: Ban Chấp Hành, Sứ mệnh & Hoạt động, Bằng khen & Thành tích,
    Thư viện ảnh hoạt động của LCĐ, CLB trực thuộc và Kênh mạng xã hội.
    """
    faculties = load_faculty_data()
    clean_code = code.strip().rstrip('/').lower()
    
    target_faculty = None
    for fac in faculties:
        fid = fac.get('id', '').lower()
        aliases = [a.lower() for a in fac.get('aliases', [])]
        if fid == clean_code or clean_code in aliases:
            target_faculty = fac
            break

    if not target_faculty:
        norm_code = clean_code.replace('-', '_')
        for fac in faculties:
            if fac.get('id', '').replace('-', '_') == norm_code:
                target_faculty = fac
                break

    if not target_faculty:
        return redirect('lien_chi_doan_list')

    lcd = target_faculty.get('lcd', {})
    other_faculties = [f for f in faculties if f.get('id') != target_faculty.get('id')]
    
    all_clubs = load_clb_data()
    faculty_clubs = [c for c in all_clubs if c.get('faculty_id') == target_faculty.get('id')]
    
    return render(request, 'lien_chi_doan_detail.html', {
        'faculty': target_faculty,
        'lcd': lcd,
        'faculty_clubs': faculty_clubs,
        'other_faculties': other_faculties,
        'all_faculties': faculties,
    })

def api_khoa_list(request):
    """API trả về danh sách 9 Khoa 2026"""
    faculties = load_faculty_data()
    return JsonResponse({'status': 'success', 'data': faculties})

def api_khoa_detail(request, code):
    """API trả về chi tiết 1 Khoa"""
    faculties = load_faculty_data()
    clean_code = code.strip().rstrip('/').lower()
    for fac in faculties:
        if fac.get('id') == clean_code or clean_code in [a.lower() for a in fac.get('aliases', [])]:
            return JsonResponse({'status': 'success', 'data': fac})
    return JsonResponse({'status': 'error', 'message': 'Faculty not found'}, status=404)

# Re-export khoa view alias for compatibility
khoa = khoa_overview_view

def load_clb_data():
    clb_path = os.path.join(settings.BASE_DIR, 'data', 'clb.json')
    if os.path.exists(clb_path):
        with open(clb_path, 'r', encoding='utf-8') as f:
            clubs = json.load(f)
            for c in clubs:
                if c.get('logo'):
                    logo_file = os.path.basename(c['logo'])
                    c['logo_url'] = f'/static/img/clb/{logo_file}'
                else:
                    c['logo_url'] = None

                if c.get('cover'):
                    cover_file = os.path.basename(c['cover'])
                    c['cover_url'] = f'/static/img/clb/{cover_file}'
                else:
                    c['cover_url'] = None

                if c.get('gallery'):
                    for g in c['gallery']:
                        if isinstance(g, dict) and 'url' in g:
                            if not g['url'].startswith('/'):
                                g['url'] = f"/static/img/clb/{os.path.basename(g['url'])}"

                fid = c.get('faculty_id')
                c['faculty_name'] = FACULTY_NAMES.get(fid, 'Cấp trường') if fid else 'Cấp trường (Đoàn – Hội)'
            return clubs
    return []

def clb_view(request):
    """Trang Câu lạc bộ – Đội – Nhóm sinh viên DUE"""
    clubs = load_clb_data()
    clubs_json = json.dumps(clubs, ensure_ascii=False)
    return render(request, 'clb.html', {
        'clubs': clubs,
        'clubs_json': clubs_json,
        'clubs_count': len(clubs),
    })

def clb_detail_view(request, club_id):
    """Trang chi tiết đầy đủ thông tin chuyên sâu của một Câu lạc bộ cụ thể"""
    clubs = load_clb_data()
    clean_id = club_id.strip().rstrip('/')
    
    club = None
    for c in clubs:
        if c.get('id') == clean_id or clean_id in c.get('aliases', []):
            club = c
            break

    if not club:
        return redirect('clb')

    related = [
        c for c in clubs
        if c.get('id') != club.get('id') and (
            c.get('category') == club.get('category') or
            (c.get('faculty_id') and c.get('faculty_id') == club.get('faculty_id')) or
            c.get('level') == club.get('level')
        )
    ]
    if len(related) < 4:
        others = [c for c in clubs if c.get('id') != club.get('id') and c not in related]
        related.extend(others[:4 - len(related)])
    else:
        related = related[:4]

    return render(request, 'clb_detail.html', {
        'club': club,
        'related_clubs': related,
        'all_clubs': clubs,
    })

def sinh_vien_view(request):
    """Trang Dành cho sinh viên (gồm Đoàn - Hội, LCĐ và CLB)"""
    return clb_view(request)

def ky_tuc_xa_view(request):
    """Trang thông tin chuyên biệt Ký túc xá sinh viên DUE"""
    return render(request, 'ky_tuc_xa.html')

def hoat_dong_doan_view(request):
    """Trang thông tin chuyên biệt Hoạt động Đoàn – Hội sinh viên DUE"""
    return render(request, 'hoat_dong_doan.html')

def api_clb_list(request):
    """API trả về danh sách CLB kèm đầy đủ thông tin"""
    clubs = load_clb_data()
    return JsonResponse({'status': 'success', 'data': clubs})

def career_advisory(request):
    return render(request, 'career-advisory.html')

def chatbot(request):
    return render(request, 'chatbot.html')
