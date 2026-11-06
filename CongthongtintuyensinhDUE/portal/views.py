import json
from django.shortcuts import render, redirect
from django.http import Http404, HttpRequest, HttpResponse
from portal import selectors
from portal.models import LienChiDoan, KyTucXa, HoatDongDoan


def faculty_overview_view(request: HttpRequest) -> HttpResponse:
    """Renders the overview of faculties, institutes, and functional departments."""
    faculties = selectors.get_faculties()
    departments = selectors.get_departments()
    return render(request, 'portal/faculties.html', {
        'faculties': faculties,
        'khoa_list': faculties,
        'faculty_count': len(faculties),
        'phongban_list': departments,
    })


def faculty_detail_view(request: HttpRequest, code: str) -> HttpResponse:
    """Renders details for a specific faculty or institute matching template expectations."""
    faculties = selectors.get_faculties()
    target_faculty = selectors.get_faculty_by_code(code)
    if not target_faculty:
        return redirect('khoa')

    other_faculties = [f for f in faculties if f.get('id') != target_faculty.get('id')]
    phongban_list = selectors.get_departments()
    all_clubs = selectors.get_clubs()
    faculty_clubs = [c for c in all_clubs if c.get('faculty_id') == target_faculty.get('id')]

    return render(request, 'portal/faculty_detail.html', {
        'faculty': target_faculty,
        'other_faculties': other_faculties,
        'all_faculties': faculties,
        'phongban_list': phongban_list,
        'faculty_clubs': faculty_clubs,
    })


def faculty_lcd_detail_view(request: HttpRequest, code: str) -> HttpResponse:
    """Renders youth union (Lien Chi Doan) page for a faculty from database."""
    faculties = selectors.get_faculties()
    target_faculty = selectors.get_faculty_by_code(code)
    if not target_faculty:
        return redirect('portal:khoa')

    # Ưu tiên lấy trực tiếp từ bảng LienChiDoan trong database SQLite
    fid = target_faculty.get('id', '')
    lcd_record = LienChiDoan.objects.filter(faculty_code__iexact=fid, is_active=True).first()
    if lcd_record:
        lcd = lcd_record.to_dict()
    else:
        lcd = target_faculty.get('lcd', {})

    other_faculties = [f for f in faculties if f.get('id') != target_faculty.get('id')]
    all_clubs = selectors.get_clubs()
    faculty_clubs = [c for c in all_clubs if c.get('faculty_id') == target_faculty.get('id')]

    return render(request, 'portal/youth_union_detail.html', {
        'faculty': target_faculty,
        'lcd': lcd,
        'faculty_clubs': faculty_clubs,
        'other_faculties': other_faculties,
        'all_faculties': faculties,
    })


def lcd_overview_view(request: HttpRequest) -> HttpResponse:
    """Đã bỏ trang chung Liên Chi Đoàn theo yêu cầu người dùng, chuyển hướng về Hoạt động Đoàn."""
    return redirect('portal:hoat_dong_doan')


def club_view(request: HttpRequest) -> HttpResponse:
    """Renders student clubs list."""
    clubs = selectors.get_clubs()
    clubs_json = json.dumps(clubs, ensure_ascii=False)
    return render(request, 'portal/clubs.html', {
        'clubs': clubs,
        'clubs_json': clubs_json,
        'clubs_count': len(clubs),
    })


def club_detail_view(request: HttpRequest, club_id: str) -> HttpResponse:
    """Renders detail information for a single club."""
    clubs = selectors.get_clubs()
    club = selectors.get_club_by_id(club_id)
    if not club:
        return redirect('portal:clb')

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

    return render(request, 'portal/club_detail.html', {
        'club': club,
        'related_clubs': related,
        'all_clubs': clubs,
    })


def dormitory_view(request: HttpRequest) -> HttpResponse:
    """Renders dormitory & student housing guide directly from database."""
    ktx_list = [k.to_dict() for k in KyTucXa.objects.filter(is_active=True).order_by('order', 'id')]
    main_ktx = ktx_list[0] if ktx_list else None
    return render(request, 'portal/dormitory.html', {
        'ktx_list': ktx_list,
        'main_ktx': main_ktx,
    })


def youth_activity_view(request: HttpRequest) -> HttpResponse:
    """Renders youth union general activities directly from database."""
    activities = [a.to_dict() for a in HoatDongDoan.objects.filter(is_active=True).order_by('order', 'id')]
    return render(request, 'portal/youth_activities.html', {
        'activities': activities,
        'activities_count': len(activities),
    })


def student_life_view(request: HttpRequest) -> HttpResponse:
    """Renders student life and extracurricular portal."""
    return club_view(request)


def enrollment_guide_view(request: HttpRequest) -> HttpResponse:
    """Renders formal enrollment guide for new students."""
    return render(request, 'portal/enrollment_guide.html')


def get_freshman_schedule_events(faculty_name="Khoa Tài chính - Ngân hàng", faculty_code="tcnh"):
    """Tạo dữ liệu các mốc thời gian chi tiết của Tân sinh viên theo từng Khoa."""
    return [
        {
            "id": 1,
            "badge": "Mốc 1 • Trực tuyến",
            "badge_color": "bg-blue-50 text-blue-700 border-blue-200",
            "dot_color": "#0072BC",
            "time": "Từ 09h00 ngày 10/08 đến 17h00 ngày 15/08/2026",
            "title": "Xác nhận nhập học trực tuyến & Kê khai hồ sơ sinh viên Khóa 52K",
            "location": "Cổng thông tin tuyển sinh trực tuyến: nhaphoc.due.udn.vn",
            "desc": "Tân sinh viên tra cứu kết quả trúng tuyển chính thức bằng CCCD, điền thông tin lý lịch sinh viên điện tử, chụp ảnh thẻ sinh viên liên kết ngân hàng và nộp học phí tạm thu Học kỳ 1 theo quy định của Đại học Đà Nẵng.",
            "guide": "Sau khi hoàn thành, hệ thống sẽ cấp Mã số sinh viên (MSSV) chính thức và thông tin tài khoản Cổng sinh viên.",
            "image": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=800&q=80",
            "status": "Sắp diễn ra",
            "category": "online"
        },
        {
            "id": 2,
            "badge": "Mốc 2 • Sự kiện toàn trường",
            "badge_color": "bg-amber-50 text-amber-700 border-amber-200",
            "dot_color": "#F37021",
            "time": "08h00 - 17h30 ngày 16/08/2026 (Chủ nhật)",
            "title": "Ngày hội Chào đón Tân sinh viên DUE 2026 (Freshman Welcome Festival)",
            "location": "Khuôn viên Sân trường & Hội trường Đa năng DUE (71 Ngũ Hành Sơn)",
            "desc": "Sự kiện chào đón quy mô lớn nhất năm dành riêng cho Tân sinh viên Khóa 52K! Trải nghiệm không khí trường đại học sôi động, check-in nhận túi quà tân sinh viên (áo thun đồng phục DUE, sổ tay sinh viên, bút và sticker DUE độc quyền), hòa mình vào triển lãm hơn 13 gian hàng Câu lạc bộ và hoạt động giao lưu âm nhạc đường phố.",
            "guide": "Trang phục: Tự do, lịch sự hoặc áo cam DUE. Mang theo Giấy báo trúng tuyển hoặc CCCD để check-in nhận quà.",
            "image": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80",
            "status": "Trọng tâm",
            "category": "welcome"
        },
        {
            "id": 3,
            "badge": "Mốc 3 • Khoa chuyên môn",
            "badge_color": "bg-indigo-50 text-indigo-700 border-indigo-200",
            "dot_color": "#4338ca",
            "time": "08h30 - 11h30 ngày 18/08/2026 (Thứ Hai)",
            "title": f"Gặp mặt Ban Chủ nhiệm {faculty_name} & Cố vấn học tập",
            "location": f"Hội trường E - Giảng đường chuyên môn {faculty_name}",
            "desc": f"Buổi gặp gỡ thân mật đầu tiên giữa Thầy/Cô Lãnh đạo Khoa, các Trưởng Bộ môn và toàn thể Tân sinh viên {faculty_name}. Thầy Cô sẽ chia sẻ về chuẩn đầu ra AUN-QA, lộ trình đào tạo 4 năm, cơ hội thực tập sớm tại doanh nghiệp, trao đổi quốc tế và giới thiệu đội ngũ Giảng viên - Cố vấn học tập (GVCN) đồng hành cùng các bạn.",
            "guide": "Tân sinh viên chuẩn bị các câu hỏi về chuyên ngành, lộ trình học và cơ hội nghề nghiệp để được giải đáp trực tiếp.",
            "image": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=800&q=80",
            "status": "Quan trọng",
            "category": "faculty"
        },
        {
            "id": 4,
            "badge": "Mốc 4 • Sinh hoạt lớp",
            "badge_color": "bg-emerald-50 text-emerald-700 border-emerald-200",
            "dot_color": "#059669",
            "time": "14h00 - 16h30 ngày 18/08/2026 (Thứ Hai)",
            "title": f"Sinh hoạt Lớp Tân sinh viên & Bầu Ban cán sự lớp khóa mới - {faculty_name}",
            "location": "Phòng học chuyên ngành Nhà C & Nhà D (Phân bổ chi tiết theo từng lớp)",
            "desc": "Tân sinh viên tập trung về đúng phòng học của lớp sinh hoạt (được thông báo trên tài khoản cá nhân). Buổi sinh hoạt do Giáo viên chủ nhiệm (GVCN) chủ trì: giới thiệu làm quen các thành viên trong lớp, phổ biến nội quy học đường, tiến hành bầu Ban Cán sự lớp (Lớp trưởng, Lớp phó) và Ban Chấp hành Chi đoàn (Bí thư, Phó bí thư Chi đoàn), thành lập group Zalo/Facebook chính thức của lớp.",
            "guide": "Mỗi sinh viên chuẩn bị phần giới thiệu ngắn gọn (tên, quê quán, sở trường) để ứng cử hoặc kết nối bạn bè.",
            "image": "https://images.unsplash.com/photo-1543269865-cbf427effbad?auto=format&fit=crop&w=800&q=80",
            "status": "Bắt buộc",
            "category": "class"
        },
        {
            "id": 5,
            "badge": "Mốc 5 • Tuần SHCD",
            "badge_color": "bg-purple-50 text-purple-700 border-purple-200",
            "dot_color": "#7c3aed",
            "time": "Từ ngày 19/08 đến ngày 22/08/2026 (04 ngày)",
            "title": "Tuần sinh hoạt công dân - Học sinh, sinh viên đầu khóa năm 2026",
            "location": "Hội trường Đa năng DUE kết hợp trực tuyến MS Teams",
            "desc": "Chương trình giáo dục bắt buộc theo quy định của Bộ Giáo dục và Đào tạo. Tân sinh viên được trang bị đầy đủ kiến thức về: 1. Quy chế đào tạo đại học theo học chế tín chỉ; 2. Đăng ký môn học và điều kiện tốt nghiệp; 3. Chính sách học bổng khuyến khích, miễn giảm học phí; 4. Luật an ninh mạng, văn hóa học đường và phòng chống tệ nạn xã hội; 5. Kỹ năng thích ứng với môi trường đại học.",
            "guide": "Điểm danh đầy đủ các chuyên đề và hoàn thành bài kiểm tra trắc nghiệm thu hoạch trực tuyến (đạt >= 50/100 điểm để được cấp chứng nhận).",
            "image": "https://images.unsplash.com/photo-1577495508048-b635879837f1?auto=format&fit=crop&w=800&q=80",
            "status": "Bắt buộc Bộ GD",
            "category": "orientation"
        },
        {
            "id": 6,
            "badge": "Mốc 6 • Gala Khoa",
            "badge_color": "bg-rose-50 text-rose-700 border-rose-200",
            "dot_color": "#e11d48",
            "time": "18h30 - 21h30 ngày 23/08/2026 (Chủ nhật)",
            "title": f"Gala Chào Tân sinh viên: 'Rực Sắc Khóa Mới' - {faculty_name}",
            "location": f"Hội trường Đa năng DUE (Đơn vị tổ chức: Liên Chi Đoàn - Hội Sinh viên {faculty_name})",
            "desc": f"Đêm hội văn hóa nghệ thuật và chào đón hoành tráng nhất do Liên Chi Đoàn và Câu lạc bộ của {faculty_name} phối hợp tổ chức. Chương trình gồm: Lễ vinh danh Thủ khoa, Á khoa đầu vào năm 2026 của Khoa; Trao học bổng tài trợ của Doanh nghiệp; Các màn biểu diễn âm nhạc, nhảy hiện đại cực chất; Minigame bốc thăm trúng thưởng tai nghe Bluetooth, Balo DUE và tiệc trà teabreak giao lưu.",
            "guide": "Vé mời miễn phí được phát qua Ban Cán sự lớp và BCH Liên Chi Đoàn Khoa. Dresscode: Trẻ trung, rực rỡ.",
            "image": "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=800&q=80",
            "status": "Đặc biệt nổi bật",
            "category": "gala"
        },
        {
            "id": 7,
            "badge": "Mốc 7 • Khảo sát & Y tế",
            "badge_color": "bg-cyan-50 text-cyan-700 border-cyan-200",
            "dot_color": "#0891b2",
            "time": "08h00 - 16h30 ngày 24/08/2026 (Thứ Hai)",
            "title": "Kiểm tra phân loại Tiếng Anh đầu khóa & Khám sức khỏe sinh viên",
            "location": "Khu phòng máy Trung tâm TT&TT và Trạm Y tế DUE (Khu B)",
            "desc": "1. Kiểm tra năng lực tiếng Anh (Placement Test): Nhằm xếp lớp học phần Anh văn tổng quát và chuyên ngành phù hợp (miễn thi với thí sinh có IELTS >= 5.5). 2. Khám sức khỏe tổng quát theo quy định liên Bộ Y tế - GD&ĐT để hoàn thiện hồ sơ sinh viên và cấp thẻ bảo hiểm y tế.",
            "guide": "Mang theo CCCD, 02 ảnh thẻ 3x4 và bản sao chứng chỉ tiếng Anh (nếu có để xin miễn thi).",
            "image": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=800&q=80",
            "status": "Kiểm tra",
            "category": "test"
        },
        {
            "id": 8,
            "badge": "Mốc 8 • Ngày học đầu tiên",
            "badge_color": "bg-emerald-50 text-emerald-700 border-emerald-200",
            "dot_color": "#047857",
            "time": "Từ ngày 31/08/2026 (Thứ Hai)",
            "title": "Chính thức bước vào năm học mới - Học kỳ 1 (2026 - 2027)",
            "location": "Các giảng đường A, B, C, D, E - Trường Đại học Kinh tế, ĐHĐN",
            "desc": "Bắt đầu học kỳ học tập đầu tiên của đời sinh viên! Tân sinh viên đăng nhập cổng thông tin đào tạo tín chỉ (tinchi.due.udn.vn) để xem Thời khóa biểu chi tiết (thứ, tiết học, phòng học, giảng viên phụ trách) và tài liệu học tập của từng môn học.",
            "guide": "Chúc các bạn Tân sinh viên Khóa 52K một khởi đầu tràn đầy tự tin, nhiệt huyết và gặt hái nhiều thành tích rực rỡ tại DUE!",
            "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80",
            "status": "Học chính khóa",
            "category": "study"
        }
    ]


def faculty_freshman_schedule_view(request: HttpRequest, code: str) -> HttpResponse:
    """Renders freshman schedule customized for a specific faculty."""
    faculties = selectors.get_faculties()
    target_faculty = selectors.get_faculty_by_code(code)
    if not target_faculty:
        return redirect('lich_trinh_tan_sinh_vien')

    faculty_name = target_faculty.get('name')
    faculty_id = target_faculty.get('id')
    events = get_freshman_schedule_events(faculty_name, faculty_id)

    return render(request, 'portal/freshman_schedule.html', {
        'faculty': target_faculty,
        'faculties': faculties,
        'schedule_events': events,
        'is_faculty_specific': True,
    })


def freshman_schedule_view(request: HttpRequest) -> HttpResponse:
    """Renders freshman welcome orientation schedule (general or with faculty filter)."""
    faculties = selectors.get_faculties()
    khoa_code = request.GET.get('khoa')
    target_faculty = selectors.get_faculty_by_code(khoa_code) if khoa_code else (faculties[0] if faculties else None)

    faculty_name = target_faculty.get('name') if target_faculty else "Trường Đại học Kinh tế"
    faculty_id = target_faculty.get('id') if target_faculty else "tcnh"
    events = get_freshman_schedule_events(faculty_name, faculty_id)

    return render(request, 'portal/freshman_schedule.html', {
        'faculty': target_faculty,
        'faculties': faculties,
        'schedule_events': events,
        'is_faculty_specific': bool(khoa_code),
    })
