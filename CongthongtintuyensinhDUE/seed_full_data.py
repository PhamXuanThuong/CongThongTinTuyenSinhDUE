import os
import sys
import json
import django

# Setup Django environment
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(base_dir, '..'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CongthongtintuyensinhDUE.settings')
django.setup()

from portal.models import Faculty, Department, LienChiDoan, KyTucXa, HoatDongDoan
from admissions.models import CauLacBo

print("========================================================")
print("  SEEDING FULL DATA TO DB.SQLITE3")
print("  (Khoa, Liên Chi Đoàn, CLB, Ký Túc Xá, Hoạt Động Đoàn)")
print("========================================================")

# ----------------------------------------------------
# 1. KHOA & VIỆN ĐÀO TẠO (data/khoa.json)
# ----------------------------------------------------
khoa_json_path = os.path.join(base_dir, 'data', 'khoa.json')
if not os.path.exists(khoa_json_path):
    khoa_json_path = os.path.join(parent_dir, 'CongthongtintuyensinhDUE', 'data', 'khoa.json')

if os.path.exists(khoa_json_path):
    with open(khoa_json_path, 'r', encoding='utf-8') as f:
        khoa_data = json.load(f)
    
    print(f"\n[1/5] Đang đẩy {len(khoa_data)} Khoa/Viện vào bảng portal_faculty...")
    for idx, item in enumerate(khoa_data, start=1):
        fid = item.get('id') or item.get('code')
        defaults = {
            'name': item.get('name', ''),
            'faculty_type': item.get('type', 'faculty'),
            'url': item.get('url', ''),
            'slogan': item.get('slogan', ''),
            'intro': item.get('intro', ''),
            'mission': item.get('mission', ''),
            'vision': item.get('vision', ''),
            'history': item.get('history', ''),
            'staff_summary': item.get('staff_summary', ''),
            'dean_message': item.get('dean_message', ''),
            'formed_from': item.get('formed_from', []),
            'achievements': item.get('achievements', []),
            'career_paths': item.get('career_paths', []),
            'notable_activities': item.get('notable_activities', []),
            'leadership': item.get('leadership', {}),
            'departments': item.get('departments', []),
            'postgraduate': item.get('postgraduate', []),
            'special_programs': item.get('special_programs', []),
            'contact': item.get('contact', {}),
            'links': item.get('links', {}),
            'major_ids': item.get('major_ids', []),
            'majors_2026': item.get('majors_2026', []),
            'clubs': item.get('clubs', []),
            'why_choose': item.get('why_choose', []),
            'staff_stats': item.get('staff_stats', {}),
            'partners': item.get('partners', []),
            'student_activities': item.get('student_activities', []),
            'clubs_details': item.get('clubs_details', []),
            'gallery': item.get('gallery', []),
            'aliases': item.get('aliases', []),
            'lcd': item.get('lcd', {}),
            'icon': item.get('icon', 'school'),
            'color': item.get('color', 'bg-blue-600'),
            'border_color': item.get('border_color', ''),
            'text_color': item.get('text_color', ''),
            'light_bg': item.get('light_bg', ''),
            'gradient': item.get('gradient', 'from-blue-600 to-indigo-700'),
            'badge_color': item.get('badge_color', ''),
            'category_tag': item.get('category_tag', 'Khoa Đào tạo'),
            'order': idx,
            'is_active': True,
        }
        obj, created = Faculty.objects.update_or_create(code=fid, defaults=defaults)
        print(f"  + Khoa: {obj.name} ({'Tạo mới' if created else 'Cập nhật'})")
else:
    print(f"Không tìm thấy file {khoa_json_path}")

# ----------------------------------------------------
# 2. LIÊN CHI ĐOÀN CÁC KHOA (data/lcd-data/lien_chi_doan.json & khoa.json)
# ----------------------------------------------------
lcd_json_path = os.path.join(base_dir, 'data', 'lcd-data', 'lien_chi_doan.json')
if not os.path.exists(lcd_json_path):
    lcd_json_path = os.path.join(parent_dir, 'CongthongtintuyensinhDUE', 'data', 'lcd-data', 'lien_chi_doan.json')

lcd_data_map = {}
if os.path.exists(lcd_json_path):
    with open(lcd_json_path, 'r', encoding='utf-8') as f:
        lcd_json_obj = json.load(f)
        lcd_list_raw = lcd_json_obj.get('lien_chi_doan', []) if isinstance(lcd_json_obj, dict) else lcd_json_obj
        for d in lcd_list_raw:
            if isinstance(d, dict):
                fid = d.get('faculty_id') or d.get('id')
                if fid:
                    lcd_data_map[fid] = d

print(f"\n[2/5] Đang đẩy 9 Liên Chi Đoàn vào bảng portal_lien_chi_doan...")
all_faculties = Faculty.objects.filter(is_active=True).order_by('order')

for idx, fac in enumerate(all_faculties, start=1):
    fid = fac.code
    lcd_raw = lcd_data_map.get(fid) or fac.lcd or {}
    
    name = lcd_raw.get('name') or f"Liên Chi Đoàn {fac.name}"
    secretary = lcd_raw.get('secretary') or lcd_raw.get('bi_thu') or "ThS. Giảng viên Cố vấn Đoàn"
    deputy = lcd_raw.get('deputy_secretary') or lcd_raw.get('pho_bi_thu') or "Sinh viên Khóa 49K"
    phone = lcd_raw.get('phone') or fac.contact.get('phone', '0236 3836 169')
    email = lcd_raw.get('email') or f"lcd.{fid}@due.edu.vn"
    facebook = lcd_raw.get('facebook') or fac.contact.get('fanpage', 'https://www.facebook.com/FaceDue')
    office = lcd_raw.get('office') or f"Văn phòng Đoàn - {fac.name}"
    members = lcd_raw.get('members_count') or f"{1200 + idx*150}+ Đoàn viên"
    branches = lcd_raw.get('branches_count') or f"{20 + idx*2} Chi đoàn"
    slogan = lcd_raw.get('slogan') or "Năng động – Tiên phong – Bản lĩnh – Hội nhập"
    intro = lcd_raw.get('intro') or f"Liên Chi Đoàn {fac.name} là tổ chức Đoàn trực thuộc Đoàn TNCS Hồ Chí Minh Trường Đại học Kinh tế – Đại học Đà Nẵng, đại diện chăm lo quyền lợi và tạo sân chơi toàn diện cho toàn thể đoàn viên, sinh viên của Khoa."
    exec_board = lcd_raw.get('executive_board') or [
        {"position": "Bí thư", "name": secretary, "class": "Giảng viên", "role": "Phụ trách chung"},
        {"position": "Phó Bí thư", "name": deputy, "class": "Khóa 49K", "role": "Công tác tổ chức & Xây dựng Đoàn"},
        {"position": "Ủy viên BTV", "name": "Nguyễn Hoàng Nam", "class": "Khóa 50K", "role": "Trưởng ban Phong trào & Tình nguyện"},
        {"position": "Ủy viên BCH", "name": "Trần Thị Mai Phương", "class": "Khóa 51K", "role": "Trưởng ban Truyền thông & Sự kiện"}
    ]
    activities = lcd_raw.get('activities') or [
        {"title": f"Gala Chào đón Tân sinh viên {fac.name}", "time": "Tháng 8 - 9", "desc": "Đêm hội kết nối và chào đón tân sinh viên khóa mới."},
        {"title": "Hội thảo Học thuật và Kỹ năng nghiên cứu khoa học", "time": "Tháng 11", "desc": "Trang bị phương pháp viết bài báo NCKH và thi giải SV NCKH cấp trường."},
        {"title": "Chiến dịch Tình nguyện Đông & Áo ấm vùng cao", "time": "Tháng 12", "desc": "Trao học bổng, áo ấm và hỗ trợ đồng bào có hoàn cảnh khó khăn."},
        {"title": "Hội trại Truyền thống & Tháng Thanh Niên", "time": "Tháng 3", "desc": "Chuỗi hoạt động thể thao, kỹ năng dã ngoại và giao lưu chi đoàn."}
    ]
    images = lcd_raw.get('images') or [
        {"url": f"/static/img/khoa/{fid}_cover.jpg", "caption": f"Hoạt động phong trào {fac.name}"},
        {"url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80", "caption": "Đêm hội chào tân sinh viên"},
        {"url": "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=800&q=80", "caption": "Lễ tuyên dương cán bộ đoàn tiêu biểu"}
    ]

    lcd_obj, created = LienChiDoan.objects.update_or_create(
        faculty_code=fid,
        defaults={
            'name': name,
            'faculty_name': fac.name,
            'term': "Nhiệm kỳ 2024–2027",
            'secretary': secretary,
            'deputy_secretary': deputy,
            'phone': phone,
            'email': email,
            'facebook': facebook,
            'office': office,
            'members_count': members,
            'branches_count': branches,
            'slogan': slogan,
            'intro': intro,
            'executive_board': exec_board,
            'featured_activities': activities,
            'images': images,
            'order': idx,
            'is_active': True
        }
    )
    print(f"  + LCĐ: {lcd_obj.name} ({'Tạo mới' if created else 'Cập nhật'})")

# ----------------------------------------------------
# 3. CÂU LẠC BỘ – ĐỘI – NHÓM (data/clb.json)
# ----------------------------------------------------
clb_json_path = os.path.join(base_dir, 'data', 'clb.json')
if not os.path.exists(clb_json_path):
    clb_json_path = os.path.join(parent_dir, 'CongthongtintuyensinhDUE', 'data', 'clb.json')

if os.path.exists(clb_json_path):
    with open(clb_json_path, 'r', encoding='utf-8') as f:
        clb_data = json.load(f)
    
    print(f"\n[3/5] Đang đẩy {len(clb_data)} Câu Lạc Bộ vào bảng admissions_caulacbo...")
    for idx, c in enumerate(clb_data, start=1):
        cid = c.get('id')
        defaults = {
            'name': c.get('name', ''),
            'aliases': c.get('aliases', []),
            'level': c.get('level', 'Cấp trường'),
            'faculty_id': c.get('faculty_id') or '',
            'faculty_name': c.get('faculty_name', ''),
            'category': c.get('category', 'Học thuật'),
            'founded': str(c.get('founded', '')),
            'followers': str(c.get('followers', '')),
            'slogan': c.get('slogan', ''),
            'description': c.get('description', ''),
            'intro': c.get('intro', ''),
            'logo_url': c.get('logo_url', ''),
            'cover_url': c.get('cover_url', ''),
            'contact': c.get('contact', {}),
            'leadership': c.get('leadership', {}),
            'departments': c.get('departments', []),
            'activities': c.get('activities', []),
            'achievements': c.get('achievements', []),
            'gallery': c.get('gallery', []),
            'faq': c.get('faq', []),
            'recruitment': c.get('recruitment', ''),
            'order': idx,
            'is_active': True,
        }
        obj, created = CauLacBo.objects.update_or_create(slug=cid, defaults=defaults)
        print(f"  + CLB: {obj.name} ({'Tạo mới' if created else 'Cập nhật'})")
else:
    print(f"Không tìm thấy file {clb_json_path}")

# ----------------------------------------------------
# 4. KÝ TÚC XÁ SINH VIÊN (portal_ky_tuc_xa)
# ----------------------------------------------------
print("\n[4/5] Đang đẩy dữ liệu Ký Túc Xá vào bảng portal_ky_tuc_xa...")
ktx_records = [
    {
        'code': 'ktx-khu-d',
        'name': 'Ký Túc Xá Khu D – Trường Đại học Kinh tế (DUE)',
        'address': 'Khu D - Số 71 Ngũ Hành Sơn, Bắc Mỹ An, Ngũ Hành Sơn, Đà Nẵng (Ngay trong khuôn viên DUE)',
        'phone': '0236 3950 110',
        'email': 'kytucxa@due.edu.vn',
        'total_beds': '2.500+ Chỗ nội trú',
        'intro': 'Ký túc xá Khu D tọa lạc ngay trong khuôn viên Trường Đại học Kinh tế – Đại học Đà Nẵng, giúp sinh viên di chuyển đến giảng đường, thư viện và nhà thi đấu thể thao chỉ mất 2 phút đi bộ. Với hệ thống an ninh khép kín, camera 24/7 và khuôn viên rợp bóng cây xanh, KTX Khu D là môi trường nội trú lý tưởng hàng đầu tại Đà Nẵng.',
        'room_types': [
            {
                'type': 'Phòng Tiêu chuẩn 6 chỗ',
                'price': '350.000 VNĐ / sinh viên / tháng',
                'capacity': '6 sinh viên',
                'features': ['Giường tầng sắt có bàn học & giá sách riêng', 'Nhà vệ sinh khép kín trong phòng', 'Quạt trần & hệ thống thông gió', 'Bình nước nóng năng lượng mặt trời', 'Wifi tốc độ cao']
            },
            {
                'type': 'Phòng Tiện nghi 4 chỗ (Có điều hòa)',
                'price': '650.000 VNĐ / sinh viên / tháng',
                'capacity': '4 sinh viên',
                'features': ['Điều hòa nhiệt độ 2 chiều', 'Giường tầng cao cấp có rèm che riêng tư', 'Bình nóng lạnh riêng', 'Tủ quần áo cá nhân có khóa an toàn', 'Wifi chuyên dụng 100Mbps']
            },
            {
                'type': 'Phòng Tiết kiệm 8 chỗ',
                'price': '250.000 VNĐ / sinh viên / tháng',
                'capacity': '8 sinh viên',
                'features': ['Phòng rộng rãi, thoáng mát', '2 phòng tắm & vệ sinh khép kín', 'Giá sinh viên cực kỳ tiết kiệm', 'Hệ thống lọc nước tinh khiết uống tại vòi']
            }
        ],
        'facilities': [
            {'icon': 'wifi', 'name': 'Wifi miễn phí 24/7', 'desc': 'Đường truyền cáp quang phủ sóng toàn bộ các khối nhà KTX.'},
            {'icon': 'shield', 'name': 'An ninh & Bảo vệ 24/7', 'desc': 'Hệ thống thẻ từ ra vào, camera giám sát và đội ngũ bảo vệ thường trực.'},
            {'icon': 'local_laundry_service', 'name': 'Khu giặt sấy thông minh', 'desc': 'Khu máy giặt tự động thanh toán qua mã QR tiện lợi.'},
            {'icon': 'menu_book', 'name': 'Phòng tự học máy lạnh', 'desc': 'Không gian học tập yên tĩnh, mở cửa tự do cho sinh viên nội trú.'},
            {'icon': 'restaurant', 'name': 'Căng-tin & Cửa hàng tiện lợi', 'desc': 'Cung cấp suất ăn dinh dưỡng giá từ 25.000đ, đảm bảo ATVSTP.'},
            {'icon': 'sports_volleyball', 'name': 'Khu thể thao phức hợp', 'desc': 'Sân bóng rổ, bóng chuyền, bàn bóng bàn và khu tập gym ngoài trời.'}
        ],
        'priority_subjects': [
            '1. Sinh viên diện gia đình chính sách, con thương binh, liệt sĩ, con người có công với cách mạng.',
            '2. Sinh viên hộ nghèo, hộ cận nghèo theo quy định của Nhà nước.',
            '3. Sinh viên là người dân tộc thiểu số hoặc thường trú tại vùng sâu, vùng xa, hải đảo.',
            '4. Sinh viên đạt giải cao trong các kỳ thi HSG quốc gia, quốc tế hoặc Thủ khoa đầu vào năm 2026.',
            '5. Tân sinh viên Khóa 52K có hộ khẩu ngoài thành phố Đà Nẵng đăng ký sớm.'
        ],
        'registration_guide': [
            {'step': 1, 'title': 'Kê khai trực tuyến', 'desc': 'Tân sinh viên đăng nhập cổng kytucxa.due.udn.vn, chọn nguyện vọng loại phòng và tải lên giấy tờ ưu tiên.'},
            {'step': 2, 'title': 'Ban Quản lý xét duyệt', 'desc': 'Hệ thống đối chiếu hồ sơ và thông báo kết quả trúng tuyển KTX qua email/SMS trong vòng 48h.'},
            {'step': 3, 'title': 'Nộp kinh phí tạm thu', 'desc': 'Chuyển khoản tiền nội trú Học kỳ 1 theo mã thanh toán định danh của Đại học Đà Nẵng.'},
            {'step': 4, 'title': 'Nhận phòng & Làm thủ tục', 'desc': 'Mang CCCD và ảnh thẻ đến Văn phòng KTX Khu D để nhận chìa khóa phòng và ký biên bản nhận tài sản.'}
        ],
        'regulations': [
            'Giờ mở cửa KTX: 05h30 sáng; Giờ đóng cửa: 23h00 hàng ngày.',
            'Không nấu ăn bằng bếp gas, bếp than; chỉ sử dụng thiết bị điện an toàn được cấp phép.',
            'Không đưa người lạ vào phòng ở qua đêm; khách đến thăm phải đăng ký tại phòng bảo vệ.',
            'Giữ gìn vệ sinh chung, văn minh ký túc xá, không hút thuốc lá và không gây ồn ào sau 22h00.'
        ],
        'faq': [
            {'q': 'Tân sinh viên nộp đơn đăng ký KTX khi nào?', 'a': 'Ngay sau khi có thông báo trúng tuyển chính thức của DUE (dự kiến từ ngày 10/08/2026), cổng đăng ký KTX sẽ mở trực tuyến.'},
            {'q': 'Tiền điện nước tại KTX tính như thế nào?', 'a': 'Tiền nước sinh hoạt được miễn phí theo định mức. Tiền điện có công tơ riêng cho từng phòng và tính theo đơn giá quy định của Điện lực EVN.'},
            {'q': 'Ký túc xá có chỗ để xe máy, xe đạp không?', 'a': 'Có nhà để xe 2 tầng có mái che, thẻ từ an ninh và bảo vệ trực 24/7 với chi phí ưu đãi cho sinh viên nội trú.'}
        ],
        'image_url': 'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?auto=format&fit=crop&w=1200&q=80',
        'order': 1,
        'is_active': True
    },
    {
        'code': 'ktx-tap-trung-dh-danang',
        'name': 'Ký Túc Xá Sinh Viên Tập Trung – Đại học Đà Nẵng',
        'address': 'Khu Đô thị Đại học Đà Nẵng, Hòa Quý, Ngũ Hành Sơn, Đà Nẵng',
        'phone': '0236 3847 426',
        'email': 'ktx.udn@udn.vn',
        'total_beds': '4.000+ Chỗ nội trú',
        'intro': 'Khu KTX tập trung hiện đại quy mô lớn của Đại học Đà Nẵng, thiết kế chuẩn quốc tế với đầy đủ công viên cây xanh, thư viện thông minh, hồ bơi và tuyến xe buýt nhanh kết nối thẳng đến Trường Đại học Kinh tế (DUE).',
        'room_types': [
            {
                'type': 'Phòng Tiêu chuẩn 4 người',
                'price': '400.000 VNĐ / tháng',
                'capacity': '4 sinh viên',
                'features': ['Phòng rộng 32m2', 'Nội thất gỗ hiện đại', 'Ban công thoáng mát', 'Vệ sinh khép kín']
            },
            {
                'type': 'Phòng Studio cao cấp 2 người',
                'price': '900.000 VNĐ / tháng',
                'capacity': '2 sinh viên',
                'features': ['Điều hòa Inverter', 'Tủ lạnh mini', 'Khu bếp nấu mini khép kín', 'Bình nóng lạnh']
            }
        ],
        'facilities': [
            {'icon': 'directions_bus', 'name': 'Tuyến xe buýt nội khu', 'desc': 'Xe buýt đưa đón sinh viên từ KTX đến cơ sở DUE 71 Ngũ Hành Sơn.'},
            {'icon': 'pool', 'name': 'Bể bơi tiêu chuẩn', 'desc': 'Khu thể thao bơi lội phục vụ rèn luyện thể chất sinh viên.'},
            {'icon': 'local_hospital', 'name': 'Trạm y tế thường trực', 'desc': 'Bác sĩ trực 24/24 chăm sóc sức khỏe ban đầu.'}
        ],
        'priority_subjects': ['Ưu tiên sinh viên các trường thành viên ĐHĐN có hoàn cảnh khó khăn hoặc sinh viên quốc tế.'],
        'registration_guide': [{'step': 1, 'title': 'Đăng ký qua cổng KTX ĐHĐN', 'desc': 'Truy cập trang web ktx.udn.vn để nộp hồ sơ trực tuyến.'}],
        'regulations': ['Chấp hành nội quy chung của Đại học Đà Nẵng về khu nội trú tập trung.'],
        'faq': [{'q': 'Khoảng cách từ KTX đến trường DUE là bao xa?', 'a': 'Khoảng 7km, có tuyến xe buýt trợ giá sinh viên chạy liên tục mỗi 15 phút.'}],
        'image_url': 'https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=1200&q=80',
        'order': 2,
        'is_active': True
    }
]

for ktx in ktx_records:
    obj, created = KyTucXa.objects.update_or_create(code=ktx['code'], defaults=ktx)
    print(f"  + KTX: {obj.name} ({'Tạo mới' if created else 'Cập nhật'})")

# ----------------------------------------------------
# 5. HOẠT ĐỘNG ĐOÀN & PHONG TRÀO (portal_hoat_dong_doan)
# ----------------------------------------------------
print("\n[5/5] Đang đẩy dữ liệu Hoạt Động Đoàn vào bảng portal_hoat_dong_doan...")
doan_activities = [
    {
        'code': 'mua-he-xanh',
        'title': 'Chiến Dịch Tình Nguyện Mùa Hè Xanh',
        'category': 'Tình nguyện vì cộng đồng',
        'time_period': 'Tháng 7 hàng năm (15 - 20 ngày)',
        'scale': 'Hơn 500 chiến sĩ tình nguyện tại các xã vùng cao Quảng Nam & Đà Nẵng',
        'organizer': 'Ban Chấp hành Đoàn trường & Hội Sinh viên DUE',
        'location': 'Huyện Tây Giang, Nam Giang (Quảng Nam) và Hòa Vang (Đà Nẵng)',
        'summary': 'Mặt trận tình nguyện hè lớn nhất của tuổi trẻ DUE. Xây dựng công trình thắp sáng đường quê, sửa chữa điểm trường học, khám phát thuốc miễn phí và chuyển giao kiến thức chuyển đổi số.',
        'description': 'Mùa Hè Xanh là dấu ấn thanh xuân không thể nào quên của các thế hệ sinh viên Kinh tế. Chiến dịch tập trung vào 4 nội dung trọng tâm: 1. Xây dựng nông thôn mới và công trình thanh niên; 2. Tổ chức ôn tập văn hóa, dạy tiếng Anh và kỹ năng sống cho thiếu nhi; 3. Chuyển đổi số cộng đồng; 4. Thăm hỏi, tri ân các gia đình chính sách và Mẹ Việt Nam Anh hùng.',
        'highlights': [
            'Bàn giao 05 công trình "Thắp sáng đường quê bằng năng lượng mặt trời"',
            'Sơn sửa và nâng cấp 03 điểm trường mầm non và tiểu học vùng cao',
            'Tặng hơn 1.000 phần quà và tủ sách hiếu học cho học sinh nghèo',
            'Tập huấn bán hàng nông sản trên sàn TMĐT cho thanh niên địa phương'
        ],
        'image_url': 'https://images.unsplash.com/photo-1559027615-cd4628902d4a?auto=format&fit=crop&w=1200&q=80',
        'icon': 'wb_sunny',
        'order': 1,
        'is_active': True
    },
    {
        'code': 'tinh-nguyen-dong',
        'title': 'Chiến Dịch Tình Nguyện Đông & Xuân Tình Nguyện',
        'category': 'Tình nguyện vì cộng đồng',
        'time_period': 'Tháng 12 đến Tháng 1 hàng năm',
        'scale': 'Toàn trường, quyên góp hơn 5.000 áo ấm và quà Tết',
        'organizer': 'Đoàn trường kết hợp 9 Liên Chi Đoàn Khoa và các CLB Tình nguyện',
        'location': 'Các địa bàn miền núi khó khăn tại miền Trung - Tây Nguyên',
        'summary': 'Mang hơi ấm, áo ấm và những phần quà Tết nghĩa tình đến với bà con đồng bào dân tộc thiểu số và trẻ em vùng cao trước thềm năm mới.',
        'description': 'Chiến dịch do tuổi trẻ DUE khởi xướng nhiều năm liên tục, thu hút đông đảo sinh viên quyên góp quần áo ấm, nhu yếu phẩm, tổ chức đêm hội bánh chưng xanh và trao quà Tết tận tay người nghèo.',
        'highlights': [
            'Trao tặng 1.500 áo ấm mới và chăn ấm cho trẻ em miền núi',
            'Nấu và trao hơn 2.000 bánh chưng Tết nghĩa tình',
            'Gian hàng "0 đồng" trao nhu yếu phẩm thiết yếu cho bà con'
        ],
        'image_url': 'https://images.unsplash.com/photo-1593113598332-cd288d649433?auto=format&fit=crop&w=1200&q=80',
        'icon': 'volunteer_activism',
        'order': 2,
        'is_active': True
    },
    {
        'code': 'tiep-suc-mua-thi',
        'title': 'Chương Trình Tiếp Sức Mùa Thi & Tiếp Sức Đến Trường',
        'category': 'Hỗ trợ giáo dục',
        'time_period': 'Tháng 6 - Tháng 8 hàng năm',
        'scale': '300 tình nguyện viên tại 20 điểm thi trên địa bàn TP. Đà Nẵng',
        'organizer': 'Đoàn trường - Hội Sinh viên DUE',
        'location': 'Các điểm thi tốt nghiệp THPT và tại khuôn viên DUE đón tân sinh viên',
        'summary': 'Đồng hành cùng sĩ tử vượt vũ môn và đón tiếp, hướng dẫn tận tình cho Tân sinh viên Khóa mới trong những ngày đầu nhập học.',
        'description': 'Đội hình thanh niên tình nguyện DUE túc trực tại các bến xe, ga tàu và điểm thi để phát nước, bút viết, quạt mát, hỗ trợ phân luồng giao thông và tư vấn nhà trọ giá rẻ cho thí sinh và phụ huynh.',
        'highlights': [
            'Hỗ trợ hơn 15.000 lượt thí sinh và phụ huynh trong kỳ thi THPT',
            'Giới thiệu hơn 1.200 chỗ trọ giá rẻ, an toàn cho tân sinh viên',
            'Đội xe ôm tình nguyện "Áo xanh DUE" đưa đón sĩ tử miễn phí'
        ],
        'image_url': 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&q=80',
        'icon': 'school',
        'order': 3,
        'is_active': True
    },
    {
        'code': 'lovely-night',
        'title': 'Đêm Dạ Hội Khiêu Vũ Lovely Night',
        'category': 'Văn hóa & Nghệ thuật',
        'time_period': 'Tháng 11 hàng năm',
        'scale': 'Hơn 2.000 sinh viên tham gia',
        'organizer': 'Đoàn trường & CLB Khiêu vũ DUE',
        'location': 'Sảnh lớn Tòa nhà Đa năng DUE',
        'summary': 'Dạ hội khiêu vũ truyền thống lãng mạn, sang trọng và gắn kết, nơi sinh viên Kinh tế tự tin khoác lên mình những bộ trang phục lộng lẫy và tỏa sáng.',
        'description': 'Lovely Night là sự kiện văn hóa nghệ thuật thường niên được mong chờ nhất trong học kỳ 1. Sinh viên được trải nghiệm sàn khiêu vũ chuẩn quốc tế (Waltz, Tango, Chacha), thưởng thức các màn biểu diễn âm nhạc đặc sắc và chứng kiến đêm đăng quang của King & Queen.',
        'highlights': [
            'Cuộc thi King & Queen Dạ hội quy tụ các gương mặt tài năng, duyên dáng',
            'Không gian bài trí chuẩn dạ tiệc châu Âu sang trọng',
            'Âm nhạc giao hưởng và ban nhạc acoustic sống động'
        ],
        'image_url': 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1200&q=80',
        'icon': 'nightlife',
        'order': 4,
        'is_active': True
    },
    {
        'code': 'thu-linh-sinh-vien',
        'title': 'Hội Thi Thủ Lĩnh Sinh Viên DUE',
        'category': 'Kỹ năng & Lãnh đạo',
        'time_period': 'Tháng 3 - Tháng 4 hàng năm',
        'scale': 'Toàn thể Cán bộ Đoàn - Hội, Ban Cán sự lớp và Chủ nhiệm CLB',
        'organizer': 'Ban Thường vụ Đoàn trường DUE',
        'location': 'Hội trường A & Trung tâm Kỹ năng dã ngoại',
        'summary': 'Đấu trường tôi luyện bản lĩnh người cán bộ Đoàn - Hội, rèn luyện tư duy phản biện, kỹ năng quản lý dự án và khả năng thuyết trình trước đám đông.',
        'description': 'Trải qua các vòng thi gay cấn từ trắc nghiệm kiến thức kinh tế xã hội, tranh biện trực tiếp, đến xử lý khủng hoảng truyền thông và điều hành hoạt động thực tế, hội thi tìm kiếm và bồi dưỡng những gương mặt lãnh đạo trẻ xuất sắc cho nhà trường và xã hội.',
        'highlights': [
            'Phần thi Tranh biện đối kháng theo luật quốc tế Karl Popper',
            'Thử thách lập đề án khởi nghiệp xã hội vì cộng đồng',
            'Hành trình dã ngoại sinh tồn và kỹ năng làm việc nhóm'
        ],
        'image_url': 'https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=1200&q=80',
        'icon': 'military_tech',
        'order': 5,
        'is_active': True
    },
    {
        'code': 'hoi-thao-due',
        'title': 'Đại Hội Thể Thao Sinh Viên DUE (DUE Sports Games)',
        'category': 'Thể dục thể thao',
        'time_period': 'Tháng 4 hàng năm',
        'scale': 'Hơn 1.500 vận động viên sinh viên từ 9 Liên Chi Đoàn',
        'organizer': 'Đoàn trường & Bộ môn Giáo dục Thể chất',
        'location': 'Nhà thi đấu Đa năng & Sân bóng đá cỏ nhân tạo DUE',
        'summary': 'Giải thi đấu thể thao học đường quy mô nhất năm gồm các bộ môn: Bóng đá nam/nữ, Bóng rổ, Cầu lông, Bóng chuyền, Cờ vua và Kéo co.',
        'description': 'Hội thao là ngày hội rèn luyện sức khỏe, nêu cao tinh thần fair-play, đoàn kết giữa các Khoa chuyên môn và tuyển chọn các vận động viên xuất sắc tham dự giải thể thao sinh viên toàn quốc (VUG).',
        'highlights': [
            'Giải Bóng đá Cúp Truyền thống Kinh tế kịch tính đến phút chót',
            'Giải Bóng rổ 3x3 và 5x5 sôi động với sự cổ vũ của hàng ngàn CĐV',
            'Lễ bế mạc và trao cờ luân lưu cho Liên Chi Đoàn đoạt giải Toàn đoàn'
        ],
        'image_url': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=1200&q=80',
        'icon': 'sports_soccer',
        'order': 6,
        'is_active': True
    }
]

for act in doan_activities:
    obj, created = HoatDongDoan.objects.update_or_create(code=act['code'], defaults=act)
    print(f"  + Hoạt động: {obj.title} ({'Tạo mới' if created else 'Cập nhật'})")

print("\n========================================================")
print("  HOÀN THÀNH ĐẨY DỮ LIỆU VÀO DB.SQLITE3 THÀNH CÔNG!")
print("========================================================")
print(f"  - Tổng số Khoa/Viện (portal_faculty): {Faculty.objects.count()}")
print(f"  - Tổng số Liên Chi Đoàn (portal_lien_chi_doan): {LienChiDoan.objects.count()}")
print(f"  - Tổng số Câu Lạc Bộ (admissions_caulacbo): {CauLacBo.objects.count()}")
print(f"  - Tổng số Ký Túc Xá (portal_ky_tuc_xa): {KyTucXa.objects.count()}")
print(f"  - Tổng số Hoạt Động Đoàn (portal_hoat_dong_doan): {HoatDongDoan.objects.count()}")
print("========================================================")
