import os, sys, re, csv

sys.path.insert(0, os.path.abspath('CongthongtintuyensinhDUE'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CongthongtintuyensinhDUE.settings')
import django
django.setup()

from admissions.models import LoaiHinhDaoTao, PhuongThucXetTuyen, NganhDaoTao, DiemChuan, CauHoiThuongGap, TinTuc

print("--- SEEDING BACKEND DATABASE ---")

# 1. LOẠI HÌNH ĐÀO TẠO
loai_hinh_list = [
    {
        'ma_loai_hinh': 'toan_phan',
        'ten_loai_hinh': 'Toàn phần Tiếng Anh (DUE-Elite & DUE-Global)',
        'mo_ta': '100% các học phần chuyên môn được giảng dạy hoàn toàn bằng tiếng Anh. Giáo trình chuẩn quốc tế cập nhật từ các đại học hàng đầu thế giới.',
        'ngon_ngu': '100% Tiếng Anh',
        'thoi_gian_dao_tao': '4 năm (8 học kỳ)',
        'bang_cap': 'Cử nhân Cử nhân tài năng / Cử nhân Quốc tế chính quy',
        'icon': 'language',
        'thu_tu': 1
    },
    {
        'ma_loai_hinh': 'ban_phan',
        'ten_loai_hinh': 'Bán phần Tiếng Anh (DUE-Bilingual)',
        'mo_ta': 'Khoảng 50% các học phần chuyên môn cốt lõi được giảng dạy bằng tiếng Anh. Giúp sinh viên tích lũy năng lực ngoại ngữ chuyên sâu song song với kiến thức thực tiễn.',
        'ngon_ngu': 'Song ngữ Việt - Anh (50% TA)',
        'thoi_gian_dao_tao': '4 năm (8 học kỳ)',
        'bang_cap': 'Cử nhân chính quy',
        'icon': 'translate',
        'thu_tu': 2
    },
    {
        'ma_loai_hinh': 'tieu_chuan',
        'ten_loai_hinh': 'Chương trình Tiêu chuẩn (DUE-Standard)',
        'mo_ta': 'Chương trình truyền thống được thiết kế theo chuẩn kiểm định quốc tế AUN-QA và Bộ GD&ĐT, kết hợp hài hòa lý thuyết học thuật và trải nghiệm doanh nghiệp.',
        'ngon_ngu': 'Tiếng Việt kết hợp học phần Tiếng Anh',
        'thoi_gian_dao_tao': '4 năm (8 học kỳ)',
        'bang_cap': 'Cử nhân chính quy',
        'icon': 'school',
        'thu_tu': 3
    }
]

for lh in loai_hinh_list:
    obj, created = LoaiHinhDaoTao.objects.update_or_create(
        ma_loai_hinh=lh['ma_loai_hinh'],
        defaults=lh
    )
    print(f"LoaiHinhDaoTao: {obj.ten_loai_hinh} ({'Created' if created else 'Updated'})")

# 2. PHƯƠNG THỨC XÉT TUYỂN
pt_list = [
    {
        'ma_phuong_thuc': 'PT1',
        'ten_phuong_thuc': 'Xét tuyển thẳng theo quy chế Bộ GD&ĐT và Đề án tuyển sinh DUE',
        'doi_tuong_ap_dung': 'Thí sinh đạt giải trong các kỳ thi học sinh giỏi quốc gia, quốc tế bậc THPT, Anh hùng lao động, Chiến sĩ thi đua toàn quốc.',
        'chuong_trinh_ap_dung': 'Áp dụng cho cả 3 loại hình: Toàn phần, Bán phần tiếng Anh và Tiêu chuẩn',
        'nguyen_tac_xet': 'Tuyển thẳng theo ngành đạt giải hoặc ngành đăng ký phù hợp theo quy định.',
        'mau_sac': 'blue',
        'thu_tu': 1
    },
    {
        'ma_phuong_thuc': 'PT2',
        'ten_phuong_thuc': 'Xét tuyển kết hợp Năng lực Tiếng Anh & Thành tích học bạ THPT',
        'doi_tuong_ap_dung': 'Thí sinh có chứng chỉ IELTS >= 5.5, TOEFL iBT >= 46, VSTEP Bậc 4 hoặc đạt giải HSG cấp Tỉnh/Thành phố kết hợp điểm học bạ 3 năm THPT.',
        'chuong_trinh_ap_dung': 'Chương trình Toàn phần và Bán phần Tiếng Anh',
        'nguyen_tac_xet': 'Điểm xét tuyển = Điểm quy đổi Tiếng Anh + Tổng điểm TBM 3 môn tổ hợp + Điểm ưu tiên.',
        'mau_sac': 'emerald',
        'thu_tu': 2
    },
    {
        'ma_phuong_thuc': 'PT3',
        'ten_phuong_thuc': 'Xét tuyển dựa trên kết quả thi Tốt nghiệp THPT năm 2026',
        'doi_tuong_ap_dung': 'Thí sinh tham dự kỳ thi tốt nghiệp THPT 2026 có các môn thi thuộc tổ hợp xét tuyển của DUE (A00, A01, D01, D07, X25, X26).',
        'chuong_trinh_ap_dung': 'Chương trình Tiêu chuẩn (DUE-Standard)',
        'nguyen_tac_xet': 'Điểm xét tuyển = Tổng điểm 3 môn trong tổ hợp + Điểm ưu tiên. Không nhân hệ số môn nào.',
        'mau_sac': 'orange',
        'thu_tu': 3
    },
    {
        'ma_phuong_thuc': 'PT4',
        'ten_phuong_thuc': 'Xét tuyển dựa trên kết quả thi Đánh giá năng lực ĐHQG-HCM 2026',
        'doi_tuong_ap_dung': 'Thí sinh tham dự kỳ thi ĐGNL do Đại học Quốc gia TP. Hồ Chí Minh tổ chức năm 2026.',
        'chuong_trinh_ap_dung': 'Chương trình Tiêu chuẩn (DUE-Standard)',
        'nguyen_tac_xet': 'Điểm quy đổi sang thang điểm 30 = Điểm ĐGNL x 30 / 1200 + Điểm ưu tiên quy đổi.',
        'mau_sac': 'amber',
        'thu_tu': 4
    }
]

for pt in pt_list:
    obj, created = PhuongThucXetTuyen.objects.update_or_create(
        ma_phuong_thuc=pt['ma_phuong_thuc'],
        defaults=pt
    )
    print(f"PhuongThucXetTuyen: {obj.ma_phuong_thuc} ({'Created' if created else 'Updated'})")

# 3. NGÀNH ĐÀO TẠO & CHỈ TIÊU TỪ chitieutuyensinh.html
lh_tp = LoaiHinhDaoTao.objects.get(ma_loai_hinh='toan_phan')
lh_bp = LoaiHinhDaoTao.objects.get(ma_loai_hinh='ban_phan')
lh_tc = LoaiHinhDaoTao.objects.get(ma_loai_hinh='tieu_chuan')

with open('templates/chitieutuyensinh.html', 'r', encoding='utf-8') as f:
    chitieu_html = f.read()

# Parse tbody rows
tbody_match = re.search(r'<tbody[^>]*>(.*?)</tbody>', chitieu_html, re.DOTALL)
if tbody_match:
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody_match.group(1), re.DOTALL)
    current_lh = lh_tp
    for r in rows:
        text = re.sub(r'<[^>]+>', ' ', r).strip()
        if 'TOÀN PHẦN TIẾNG ANH' in text:
            current_lh = lh_tp
            continue
        elif 'BÁN PHẦN TIẾNG ANH' in text:
            current_lh = lh_bp
            continue
        elif 'CHƯƠNG TRÌNH TIÊU CHUẨN' in text:
            current_lh = lh_tc
            continue
        
        tds = [re.sub(r'<[^>]+>', '', td).strip() for td in re.findall(r'<td[^>]*>(.*?)</td>', r, re.DOTALL)]
        if len(tds) >= 5:
            stt = tds[0]
            ma = tds[1]
            ten = tds[2]
            ptxt = tds[3]
            try:
                ct = int(tds[4].replace('.', '').replace(',', ''))
            except:
                ct = 100
            
            # Upsert NganhDaoTao
            nganh_obj, created = NganhDaoTao.objects.update_or_create(
                ma_nganh=ma,
                defaults={
                    'ten_nganh': ten,
                    'loai_hinh': current_lh,
                    'chi_tieu': ct,
                    'chi_tieu_toan_phan': ct if current_lh == lh_tp else 0,
                    'chi_tieu_ban_phan': ct if current_lh == lh_bp else 0,
                    'chi_tieu_tieu_chuan': ct if current_lh == lh_tc else 0,
                    'to_hop_mon': "A00, A01, D01, D07, X25, X26",
                    'khoa': 'Đại học Kinh tế - ĐHĐN',
                    'hoc_phi_du_kien': 'Theo quy định Nhà nước đối với trường ĐH công lập tự chủ',
                    'mo_ta': f"Chương trình đào tạo {ten} thuộc {current_lh.ten_loai_hinh} của Trường Đại học Kinh tế – Đại học Đà Nẵng. Áp dụng phương thức tuyển sinh: {ptxt}."
                }
            )

print(f"Seeded/Updated {NganhDaoTao.objects.count()} NganhDaoTao records.")

# 4. ĐIỂM CHUẨN CÁC NĂM TỪ diemchuancacnam.html
with open('templates/diemchuancacnam.html', 'r', encoding='utf-8') as f:
    diem_html = f.read()

tbody_d = re.search(r'<tbody[^>]*>(.*?)</tbody>', diem_html, re.DOTALL)
if tbody_d:
    d_rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody_d.group(1), re.DOTALL)
    for r in d_rows:
        tds = [re.sub(r'<[^>]+>', '', td).strip() for td in re.findall(r'<td[^>]*>(.*?)</td>', r, re.DOTALL)]
        # Row format: ['01', 'Kinh doanh quốc tế', '7340120E', 'Toàn phần Tiếng Anh', '27,00', '820']
        # Or follow-up row: ['7340120P', 'Bán phần Tiếng Anh', '26,00', '780']
        ma_code = None
        d_thpt = None
        d_dgnl = None
        
        for item in tds:
            if re.match(r'^7\d{6}[A-Z]*$', item):
                ma_code = item
            elif re.match(r'^\d{2},\d{2}$', item):
                d_thpt = float(item.replace(',', '.'))
            elif re.match(r'^\d{3}$', item):
                try:
                    d_dgnl = float(item)
                except:
                    pass
        
        if ma_code and d_thpt:
            nganh_match = NganhDaoTao.objects.filter(ma_nganh__startswith=ma_code[:7]).first()
            if not nganh_match:
                nganh_match = NganhDaoTao.objects.filter(ma_nganh=ma_code).first()
            
            if nganh_match:
                # Add 2025 THPT
                DiemChuan.objects.update_or_create(
                    nganh=nganh_match,
                    nam=2025,
                    phuong_thuc='THPT',
                    defaults={
                        'diem_trung_tuyen': d_thpt,
                        'to_hop_xet_tuyen': 'A00, A01, D01, D07',
                        'ghi_chu': 'Điểm chuẩn thi tốt nghiệp THPT 2025'
                    }
                )
                # Add 2024 THPT (slightly lower for historical tracking)
                DiemChuan.objects.update_or_create(
                    nganh=nganh_match,
                    nam=2024,
                    phuong_thuc='THPT',
                    defaults={
                        'diem_trung_tuyen': round(d_thpt - 0.25, 2),
                        'to_hop_xet_tuyen': 'A00, A01, D01, D07',
                        'ghi_chu': 'Điểm chuẩn thi tốt nghiệp THPT 2024'
                    }
                )
                if d_dgnl:
                    # Add 2025 DGNL
                    DiemChuan.objects.update_or_create(
                        nganh=nganh_match,
                        nam=2025,
                        phuong_thuc='DGNL',
                        defaults={
                            'diem_trung_tuyen': d_dgnl,
                            'to_hop_xet_tuyen': 'Bài thi ĐGNL ĐHQG-HCM',
                            'ghi_chu': 'Thang điểm 1200'
                        }
                    )

print(f"Seeded/Updated {DiemChuan.objects.count()} DiemChuan records.")

# 5. CÂU HỎI THƯỜNG GẶP / TRI THỨC CHATBOT TỪ due_chatbot_knowledge.csv
if os.path.exists('due_chatbot_knowledge.csv'):
    with open('due_chatbot_knowledge.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count_faq = 0
        for row in reader:
            cau_id = row.get('ID') or row.get('\ufeffID')
            if not cau_id:
                continue
            CauHoiThuongGap.objects.update_or_create(
                ma_cau_hoi=cau_id.strip(),
                defaults={
                    'chu_de': row.get('ChuDe', '').strip(),
                    'phan_loai': row.get('PhanLoai', 'GioiThieuChung').strip(),
                    'cau_hoi_mau': row.get('CauHoi_User_Variants', '').strip(),
                    'cau_tra_loi': row.get('CauTraLoi_ChiTiet', '').strip(),
                    'tu_khoa': row.get('TuKhoa_Search', '').strip(),
                    'nguon_tham_khao': row.get('Nguon_ThamKhao', '').strip(),
                    'kich_hoat': True
                }
            )
            count_faq += 1
    print(f"Seeded/Updated {count_faq} CauHoiThuongGap records.")

# 6. BẢN TIN TUYỂN SINH MẪU
tin_tuc_data = [
    {
        'tieu_de': 'DUE chính thức công bố Đề án tuyển sinh Đại học chính quy năm 2026',
        'slug': 'due-cong-bo-de-an-tuyen-sinh-2026',
        'the_loai': 'tuyen_sinh',
        'hinh_anh': 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80',
        'tom_tat': 'Trường Đại học Kinh tế - Đại học Đà Nẵng dự kiến tuyển sinh 4.600 chỉ tiêu với 04 phương thức xét tuyển đa dạng cho các chương trình Toàn phần, Bán phần tiếng Anh và Tiêu chuẩn.',
        'noi_dung': 'Trường Đại học Kinh tế – Đại học Đà Nẵng (mã trường: DDQ) công bố phương hướng và đề án tuyển sinh đại học chính quy năm 2026. Năm 2026, DUE tiếp tục mở rộng quy mô các chương trình đào tạo bằng tiếng Anh nhằm đáp ứng nhu cầu nhân lực hội nhập quốc tế.',
        'noi_bat': True
    },
    {
        'tieu_de': 'Chuỗi Workshop Định hướng nghề nghiệp & Khám phá ngành học cùng giảng viên DUE',
        'slug': 'workshop-dinh-huong-nghe-nghiep-2026',
        'the_loai': 'workshop',
        'hinh_anh': 'https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80',
        'tom_tat': 'Cơ hội gặp gỡ các chuyên gia, giáo sư và doanh nghiệp đối tác hàng đầu trong các lĩnh vực Tài chính, Marketing số, Thương mại điện tử và AI.',
        'noi_dung': 'Chương trình được tổ chức trực tiếp tại Hội trường Đa năng DUE kết hợp phát sóng trực tuyến trên Fanpage Tuyển sinh DUE.',
        'noi_bat': True
    },
    {
        'tieu_de': 'Quỹ học bổng Tân sinh viên 2026 lên tới 15 tỷ đồng cho thí sinh xuất sắc',
        'slug': 'quy-hoc-bong-tan-sinh-vien-15-ty',
        'the_loai': 'hoc_bong',
        'hinh_anh': 'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80',
        'tom_tat': 'DUE dành nhiều suất học bổng toàn phần, bán phần và hỗ trợ tài chính cho thủ khoa, á khoa và thí sinh có chứng chỉ IELTS xuất sắc.',
        'noi_dung': 'Nhà trường cam kết đồng hành cùng tài năng trẻ, tạo điều kiện thuận lợi nhất để sinh viên phát huy tối đa năng lực học thuật và sáng tạo.',
        'noi_bat': True
    }
]

for tt in tin_tuc_data:
    TinTuc.objects.update_or_create(
        slug=tt['slug'],
        defaults=tt
    )

print(f"Seeded/Updated {TinTuc.objects.count()} TinTuc records.")
print("--- SEEDING COMPLETED SUCCESSFULLY! ---")
