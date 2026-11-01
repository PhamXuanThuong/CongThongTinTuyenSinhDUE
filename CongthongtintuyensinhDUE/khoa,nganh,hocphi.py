import os
import sys
import csv
import django

# Setup Django
sys.path.append(r'e:\CongThongTinTuyenSinhDUE\CongthongtintuyensinhDUE')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CongthongtintuyensinhDUE.settings')
django.setup()

from tuyensinh.models import KhoaPhongBan, ChuyenNganh, BangHocPhi, CauHoiHocPhi

def build_dataset():
    records = []
    current_id = 1

    # 1. THÔNG TIN CHUNG VỀ TRƯỜNG ĐẠI HỌC KINH TẾ - ĐH ĐÀ NẴNG (DUE)
    records.append({
        "id": f"KB-CHUNG-{current_id:03d}",
        "loai_thong_tin": "Thông tin chung về Trường",
        "ten_chu_de": "Trường Đại học Kinh tế - Đại học Đà Nẵng (DUE)",
        "khoa_don_vi_quan_ly": "Ban Giám hiệu - Trường Đại học Kinh tế",
        "ma_dinh_danh_hoac_ma_nganh": "DUE - DDK",
        "khau_hieu_dinh_huong": "Nơi nuôi dưỡng đam mê, kiến tạo tương lai - Cơ sở giáo dục đại học đạt chuẩn quốc tế",
        "mo_ta_tong_quan": "Trường Đại học Kinh tế - Đại học Đà Nẵng (DUE) là trường đại học công lập đa ngành, trường đầu ngành về đào tạo khối ngành kinh tế, quản lý và luật tại khu vực Miền Trung - Tây Nguyên và cả nước. Trường đạt chuẩn kiểm định chất lượng quốc tế và quốc gia (AUN-QA, Bộ GD&ĐT).",
        "cac_chuyen_nganh_dao_tao": "Đào tạo hơn 50 chuyên ngành đại học thuộc 12 Khoa chuyên môn; các chương trình Cử nhân Tiêu chuẩn, Cử nhân Tài năng, Bán phần tiếng Anh và Toàn phần tiếng Anh.",
        "co_hoi_nghe_nghiep_chuc_nang": "Tỷ lệ sinh viên có việc làm sau tốt nghiệp đạt trên 95% tại các ngân hàng lớn, tập đoàn tài chính, tập đoàn đa quốc gia, công ty kiểm toán Big 4, doanh nghiệp logistics và cơ quan nhà nước.",
        "chi_tiet_hoc_phi_hoac_huong_dan": "Học phí đại học chính quy từ 29.5 triệu VNĐ/năm tùy chương trình đào tạo; thu theo từng học kỳ dựa trên tín chỉ thực tế.",
        "dia_diem_phong_lam_viec": "Số 71 Ngũ Hành Sơn, Phường Mỹ An, Quận Ngũ Hành Sơn, TP. Đà Nẵng",
        "so_dien_thoai_hotline": "0236 3836 169 - 0236 3950 115",
        "email_lien_he": "tuyensinh@due.edu.vn",
        "link_fanpage_messenger": "https://www.facebook.com/FaceDue | https://m.me/FaceDue",
        "cau_hoi_mau_cho_chatbot": "Địa chỉ trường DUE ở đâu? Trường Đại học Kinh tế Đà Nẵng có những ngành nào? Hotline tư vấn tuyển sinh DUE là số mấy? Trường DUE có tốt không?"
    })
    current_id += 1

    # 2. CÁC KHOA ĐÀO TẠO & PHÒNG BAN CHỨC NĂNG (TỔNG QUAN)
    departments = KhoaPhongBan.objects.all().prefetch_related('majors').order_by('category', 'order', 'id')
    for d in departments:
        category_name = "Khoa Đào Tạo" if d.category == 'khoa' else "Phòng Ban Chức Năng / Trung Tâm"
        majors_list = [f"{m.name} ({m.note})" if m.note else m.name for m in d.majors.all()]
        majors_str = "; ".join(majors_list) if majors_list else "Không áp dụng"

        if d.category == 'khoa':
            prompt_samples = f"Khoa {d.name} có những ngành nào? Học {d.name} ra trường làm gì? Mã ngành của {d.name}? Liên hệ khoa {d.name} thế nào?"
        else:
            prompt_samples = f"Chức năng của {d.name}? Địa chỉ phòng làm việc của {d.name}? Số điện thoại liên hệ {d.name}? Hỗ trợ sinh viên tại {d.name}."

        records.append({
            "id": f"KB-DONVI-{current_id:03d}",
            "loai_thong_tin": category_name,
            "ten_chu_de": d.name,
            "khoa_don_vi_quan_ly": d.name,
            "ma_dinh_danh_hoac_ma_nganh": d.code,
            "khau_hieu_dinh_huong": d.tagline or "Đào tạo chất lượng cao chuẩn quốc tế",
            "mo_ta_tong_quan": d.description,
            "cac_chuyen_nganh_dao_tao": majors_str,
            "co_hoi_nghe_nghiep_chuc_nang": d.careers_or_functions,
            "chi_tiet_hoc_phi_hoac_huong_dan": "Áp dụng theo khung học phí cử nhân chính quy của Trường Đại học Kinh tế (tùy theo chương trình Tiêu chuẩn, Bán phần TA, Toàn phần TA hoặc Tài năng).",
            "dia_diem_phong_lam_viec": d.location,
            "so_dien_thoai_hotline": d.phone or "0236 3836 169",
            "email_lien_he": d.email or "tuyensinh@due.edu.vn",
            "link_fanpage_messenger": f"{d.fanpage_url} | {d.messenger_url}",
            "cau_hoi_mau_cho_chatbot": prompt_samples
        })
        current_id += 1

    # 3. CHI TIẾT TỪNG CHUYÊN NGÀNH ĐÀO TẠO (56 CHUYÊN NGÀNH)
    majors = ChuyenNganh.objects.all().select_related('khoa').order_by('khoa__order', 'order', 'id')
    for m in majors:
        khoa = m.khoa
        is_faculty = (khoa.category == 'khoa')
        loai_tt = "Chuyên ngành Đào tạo" if is_faculty else "Hoạt động & Dịch vụ Đơn vị"

        record_desc = (
            f"Chuyên ngành/định hướng '{m.name}' trực thuộc {khoa.name}. "
            f"{khoa.description}"
        )
        record_career = (
            f"Cơ hội việc làm sau tốt nghiệp chuyên ngành {m.name}: {khoa.careers_or_functions}"
            if is_faculty else f"Chức năng phục vụ người học: {khoa.careers_or_functions}"
        )

        sample_prompts = (
            f"Ngành {m.name} học gì? Mã ngành {m.name} là bao nhiêu? "
            f"Học {m.name} trực thuộc khoa nào? Ra trường làm ở đâu đối với ngành {m.name}?"
        ) if is_faculty else f"Dịch vụ {m.name} tại {khoa.name} hỗ trợ sinh viên những gì?"

        records.append({
            "id": f"KB-NGANH-{current_id:03d}",
            "loai_thong_tin": loai_tt,
            "ten_chu_de": m.name,
            "khoa_don_vi_quan_ly": khoa.name,
            "ma_dinh_danh_hoac_ma_nganh": m.note or khoa.code,
            "khau_hieu_dinh_huong": khoa.tagline or "Đào tạo chuẩn thực tiễn và hội nhập quốc tế",
            "mo_ta_tong_quan": record_desc,
            "cac_chuyen_nganh_dao_tao": m.name,
            "co_hoi_nghe_nghiep_chuc_nang": record_career,
            "chi_tiet_hoc_phi_hoac_huong_dan": "Thu theo tín chỉ đăng ký thực tế. Mức học phí năm 1 từ 29.5 triệu đồng (chương trình tiêu chuẩn), hoặc theo chương trình tiếng Anh / tài năng tương ứng.",
            "dia_diem_phong_lam_viec": khoa.location,
            "so_dien_thoai_hotline": khoa.phone or "0236 3836 169",
            "email_lien_he": khoa.email or "tuyensinh@due.edu.vn",
            "link_fanpage_messenger": f"{khoa.fanpage_url} | {khoa.messenger_url}",
            "cau_hoi_mau_cho_chatbot": sample_prompts
        })
        current_id += 1

    # 4. BẢNG MỨC HỌC PHÍ THEO TỪNG CHƯƠNG TRÌNH
    tuition_rows = BangHocPhi.objects.all().order_by('order')
    for t in tuition_rows:
        y1 = float(t.nam_hoc_1)
        y2 = float(t.nam_hoc_2)
        y3 = float(t.nam_hoc_3)
        y4 = float(t.nam_hoc_4)
        term_y1 = round(y1 / 2, 2)
        total_4y = round(y1 + y2 + y3 + y4, 2)

        hoc_phi_detail = (
            f"Lộ trình 4 năm (Triệu VNĐ/năm): "
            f"Năm 1 (2026-2027): {y1} tr VNĐ (~{term_y1} tr/học kỳ); "
            f"Năm 2 (2027-2028): {y2} tr VNĐ; "
            f"Năm 3 (2028-2029): {y3} tr VNĐ; "
            f"Năm 4 (2029-2030): {y4} tr VNĐ. "
            f"Tổng học phí toàn khóa 4 năm ước tính: {total_4y} triệu VNĐ."
        )

        records.append({
            "id": f"KB-HOCPHI-{current_id:03d}",
            "loai_thong_tin": "Bảng Học Phí Chương Trình Đào Tạo",
            "ten_chu_de": f"Học phí chương trình {t.nhom}",
            "khoa_don_vi_quan_ly": "Phòng Kế hoạch - Tài chính & Ban Tuyển sinh DUE",
            "ma_dinh_danh_hoac_ma_nganh": t.slug,
            "khau_hieu_dinh_huong": "Công khai, minh bạch theo lộ trình toàn khóa",
            "mo_ta_tong_quan": f"Mức học phí áp dụng cho sinh viên trúng tuyển khóa tuyển sinh năm 2026 đối với chương trình: {t.nhom}. Mức học phí được quy định cụ thể từng năm theo quy định cơ sở giáo dục tự chủ của Chính phủ.",
            "cac_chuyen_nganh_dao_tao": "Áp dụng cho tất cả các chuyên ngành thuộc chương trình đào tạo này.",
            "co_hoi_nghe_nghiep_chuc_nang": "Chương trình đào tạo chất lượng cao, trang bị kiến thức chuyên sâu và năng lực ngoại ngữ vượt trội.",
            "chi_tiet_hoc_phi_hoac_huong_dan": hoc_phi_detail,
            "dia_diem_phong_lam_viec": "Phòng Kế hoạch - Tài chính (Tầng 1 Nhà A, Trường ĐH Kinh tế)",
            "so_dien_thoai_hotline": "0236 3836 172 - 0236 3836 169",
            "email_lien_he": "khtc@due.edu.vn",
            "link_fanpage_messenger": "https://www.facebook.com/FaceDue | https://m.me/FaceDue",
            "cau_hoi_mau_cho_chatbot": f"Học phí {t.nhom} bao nhiêu tiền một năm? Học phí 1 kỳ của {t.slug} là bao nhiêu? Lộ trình 4 năm của {t.nhom}? Tổng học phí 4 năm {t.slug}?"
        })
        current_id += 1

    # 5. CHÍNH SÁCH HỌC BỔNG - MIỄN GIẢM HỌC PHÍ - VAY VỐN
    scholarship_policies = [
        {
            "ten": "Chính sách Học bổng Thủ khoa, Á khoa Tuyển sinh",
            "dinh_huong": "Tuyên dương và thu hút nhân tài xuất sắc",
            "mo_ta": "Trường Đại học Kinh tế - ĐH Đà Nẵng trao học bổng toàn phần miễn 100% học phí năm học đầu tiên cho các thí sinh đỗ Thủ khoa, Á khoa theo các phương thức tuyển sinh của Trường.",
            "chi_tiet": "Miễn 100% học phí năm thứ nhất (tương đương 2 học kỳ chính). Trong các năm tiếp theo, sinh viên duy trì kết quả học tập và rèn luyện tốt sẽ tiếp tục được xét học bổng Khuyến khích học tập loại Xuất sắc.",
            "faq_prompts": "Thủ khoa DUE có được học bổng không? Điều kiện nhận học bổng tuyển sinh 100% học phí? Học bổng á khoa DUE là bao nhiêu?"
        },
        {
            "ten": "Chính sách Học bổng Khuyến khích học tập định kỳ",
            "dinh_huong": "Khen thưởng kết quả học tập và rèn luyện mỗi học kỳ",
            "mo_ta": "Nhà trường trích tối thiểu 8% từ nguồn thu học phí để lập quỹ học bổng khuyến khích học tập xét cấp cho sinh viên sau mỗi học kỳ chính (Kỳ 1 và Kỳ 2).",
            "chi_tiet": "Phân thành 3 mức học bổng: Loại Xuất sắc (bằng hoặc cao hơn 100% mức học phí), Loại Giỏi, Loại Khá. Tiêu chí căn cứ vào Điểm trung bình chung học tập (GPA) và Điểm rèn luyện của học kỳ đó.",
            "faq_prompts": "Học bổng khuyến khích học tập DUE tính thế nào? Điểm bao nhiêu được học bổng ở DUE? Học bổng xuất sắc được bao nhiêu tiền?"
        },
        {
            "ten": "Chính sách Học bổng Doanh nghiệp & Cựu sinh viên tài trợ",
            "dinh_huong": "Kết nối doanh nghiệp - Đồng hành cùng thế hệ trẻ",
            "mo_ta": "Hàng trăm suất học bổng tài trợ thường niên từ các ngân hàng (Vietcombank, BIDV, Agribank), các tập đoàn đa quốc gia, công ty kiểm toán Big 4, và mạng lưới cựu sinh viên DUE thành đạt.",
            "chi_tiet": "Mức học bổng từ 5.000.000 VNĐ đến 20.000.000 VNĐ/suất hoặc tài trợ toàn phần khóa học tiếng Anh, tin học quốc tế và cơ hội thực tập, tuyển dụng trực tiếp.",
            "faq_prompts": "DUE có học bổng doanh nghiệp không? Làm thế nào để xin học bổng tài trợ tại DUE? Doanh nghiệp nào tài trợ học bổng cho sinh viên DUE?"
        },
        {
            "ten": "Chính sách Miễn giảm học phí theo Nghị định của Chính phủ",
            "dinh_huong": "Đảm bảo công bằng xã hội và an sinh giáo dục",
            "mo_ta": "Thực hiện đầy đủ các chế độ miễn, giảm học phí cho người học theo Nghị định số 81/2021/NĐ-CP và các văn bản hướng dẫn hiện hành của Chính phủ.",
            "chi_tiet": "Đối tượng miễn 100% học phí: Con liệt sĩ, con thương binh/bệnh binh nặng, sinh viên khuyết tật, sinh viên dân tộc thiểu số rất ít người thuộc hộ nghèo/cận nghèo. Đối tượng giảm 70% và 50% học phí theo quy định nhà nước. Sinh viên nộp hồ sơ tại Phòng Công tác sinh viên vào đầu mỗi năm học.",
            "faq_prompts": "Con thương binh có được miễn học phí ở DUE không? Hộ nghèo được giảm bao nhiêu học phí tại DUE? Hồ sơ xin miễn giảm học phí nộp ở đâu và khi nào?"
        },
        {
            "ten": "Chính sách Hỗ trợ vay vốn tín dụng học tập ưu đãi (NHCSXH)",
            "dinh_huong": "Tiếp sức đến trường - Không để sinh viên vì khó khăn mà bỏ học",
            "mo_ta": "Nhà trường hỗ trợ xác nhận thủ tục vay vốn tín dụng sinh viên theo chương trình tín dụng học sinh, sinh viên của Ngân hàng Chính sách xã hội (VBSP) theo Quyết định của Thủ tướng Chính phủ.",
            "chi_tiet": "Mức vay tối đa lên tới 4.000.000 VNĐ/tháng (40.000.000 VNĐ/năm học) với lãi suất ưu đãi đặc biệt của Nhà nước. Sinh viên xin giấy xác nhận tại Phòng Công tác sinh viên (Tổ 1 cửa) để nộp về Ngân hàng CSXH tại địa phương cư trú.",
            "faq_prompts": "Làm thủ tục vay vốn sinh viên ở DUE thế nào? Giấy vay vốn sinh viên xin ở đâu? Mức vay tín dụng sinh viên tối đa là bao nhiêu?"
        },
        {
            "ten": "Chính sách Gia hạn đóng học phí cho sinh viên khó khăn đột xuất",
            "dinh_huong": "Hỗ trợ kịp thời, tạo điều kiện học tập tốt nhất",
            "mo_ta": "Sinh viên có gia đình gặp biến cố tài chính hoặc khó khăn kinh tế đột xuất trong kỳ học có thể làm đơn xin hoãn/gia hạn thời gian nộp học phí.",
            "chi_tiet": "Sinh viên nộp đơn xin gia hạn học phí tại Phòng Công tác sinh viên trước thời hạn chót nộp học phí của học kỳ. Sau khi được phê duyệt, sinh viên vẫn được duy trì đăng ký tín chỉ và tham gia thi kết thúc học phần bình thường.",
            "faq_prompts": "Chưa có tiền đóng học phí có được gia hạn không? Làm đơn xin gia hạn học phí nộp cho ai? Không đóng học phí đúng hạn có bị cấm thi không?"
        }
    ]

    for p in scholarship_policies:
        records.append({
            "id": f"KB-CHINHSACH-{current_id:03d}",
            "loai_thong_tin": "Chính Sách Học Bổng & Hỗ Trợ Sinh Viên",
            "ten_chu_de": p["ten"],
            "khoa_don_vi_quan_ly": "Phòng Công tác sinh viên & Phòng Kế hoạch - Tài chính",
            "ma_dinh_danh_hoac_ma_nganh": "chinh-sach-ho-tro",
            "khau_hieu_dinh_huong": p["dinh_huong"],
            "mo_ta_tong_quan": p["mo_ta"],
            "cac_chuyen_nganh_dao_tao": "Áp dụng cho toàn bộ sinh viên chính quy trường DUE.",
            "co_hoi_nghe_nghiep_chuc_nang": "Giảm bớt gánh nặng kinh tế cho gia đình, khích lệ sinh viên phấn đấu học tập đạt thành tích xuất sắc.",
            "chi_tiet_hoc_phi_hoac_huong_dan": p["chi_tiet"],
            "dia_diem_phong_lam_viec": "Phòng Công tác sinh viên (Tổ 1 cửa, Tầng 1 Nhà H, DUE)",
            "so_dien_thoai_hotline": "0236 3836 179 - 0236 3950 115",
            "email_lien_he": "ctsv@due.edu.vn",
            "link_fanpage_messenger": "https://www.facebook.com/due.ctsv | https://m.me/FaceDue",
            "cau_hoi_mau_cho_chatbot": p["faq_prompts"]
        })
        current_id += 1

    # 6. HƯỚNG DẪN ĐÓNG HỌC PHÍ & PHƯƠNG THỨC THANH TOÁN
    payment_methods = [
        {
            "ten": "Quy định Đóng học phí theo Học kỳ và Tín chỉ",
            "mo_ta": "Học phí tại DUE được thu theo từng học kỳ dựa trên tổng số tín chỉ thực tế mà sinh viên đăng ký học trong kỳ đó. Một năm học tiêu chuẩn gồm 2 học kỳ chính (Kỳ 1 và Kỳ 2), và 1 học kỳ phụ (kỳ hè tự nguyện để học vượt hoặc cải thiện điểm).",
            "chi_tiet": "Số tiền mỗi kỳ = Số tín chỉ đăng ký x Đơn giá 1 tín chỉ của chương trình tương ứng. Trung bình mỗi học kỳ sinh viên đăng ký khoảng 15 - 20 tín chỉ, tương đương khoảng 1/2 mức học phí niêm yết theo năm.",
            "prompts": "Học phí DUE đóng theo năm hay theo kỳ? Cách tính tiền học phí theo tín chỉ ở DUE? Kỳ hè có bắt buộc học và đóng học phí không?"
        },
        {
            "ten": "Cổng Thanh toán Trực tuyến E-Payment DUE (VietQR / Thẻ ATM)",
            "mo_ta": "Sinh viên và phụ huynh nộp học phí 100% trực tuyến qua Cổng thanh toán điện tử của Trường Đại học Kinh tế: https://epayment.due.udn.vn",
            "chi_tiet": "Các bước nộp: Bước 1: Truy cập https://epayment.due.udn.vn -> Bước 2: Nhập Mã số sinh viên (MSSV) để tra cứu công nợ -> Bước 3: Chọn phương thức quét mã VietQR tự động khớp lệnh ngay lập tức hoặc thanh toán qua thẻ nội địa VNPAY / thẻ quốc tế Visa, Master -> Bước 4: Hệ thống tự động gạch nợ sau 30 giây và gửi biên lai xác nhận điện tử.",
            "prompts": "Cách nộp học phí DUE trực tuyến? Nộp học phí qua cổng epayment due udn vn thế nào? Quét mã VietQR nộp học phí DUE có được không?"
        },
        {
            "ten": "Nộp học phí qua Ứng dụng Mobile Banking các Ngân hàng liên kết",
            "mo_ta": "Nhà trường liên kết trực tiếp với các ngân hàng thương mại lớn: Agribank, Vietcombank, BIDV, VietinBank để thu học phí tự động.",
            "chi_tiet": "Trên App Mobile Banking của ngân hàng, chọn mục 'Thanh toán hóa đơn' -> Chọn 'Học phí' -> Chọn 'Đại học Kinh tế - ĐH Đà Nẵng' -> Nhập Mã số sinh viên (MSSV). Tên sinh viên và số tiền học phí cần nộp sẽ tự động hiển thị chính xác để người nộp bấm xác nhận chuyển tiền.",
            "prompts": "Nộp học phí DUE qua ngân hàng nào? Cách nộp học phí DUE trên app Agribank / Vietcombank / Vietinbank? Số tài khoản nộp học phí của DUE là gì?"
        },
        {
            "ten": "Quy định Hóa đơn điện tử và Biên lai thu học phí",
            "mo_ta": "100% các khoản thu học phí tại DUE đều được phát hành Hóa đơn điện tử hợp pháp theo quy định của Tổng cục Thuế và Bộ Tài chính.",
            "chi_tiet": "Sau khi giao dịch thanh toán thành công, hệ thống tài chính sẽ tự động xuất Hóa đơn điện tử có mã của cơ quan thuế và gửi bản sao về địa chỉ Email sinh viên (@due.edu.vn) để lưu trữ hoặc xuất trình cho cơ quan công tác của phụ huynh thanh toán.",
            "prompts": "Sau khi nộp học phí có được cấp hóa đơn đỏ không? Lấy hóa đơn điện tử học phí DUE ở đâu? Tra cứu hóa đơn học phí DUE thế nào?"
        }
    ]

    for pm in payment_methods:
        records.append({
            "id": f"KB-THANHTOAN-{current_id:03d}",
            "loai_thong_tin": "Phương Thức Nộp Học Phí & Kế Toán",
            "ten_chu_de": pm["ten"],
            "khoa_don_vi_quan_ly": "Phòng Kế hoạch - Tài chính",
            "ma_dinh_danh_hoac_ma_nganh": "thanh-toan-hoc-phi",
            "khau_hieu_dinh_huong": "Nhanh chóng - Tiện lợi - An toàn 100% không dùng tiền mặt",
            "mo_ta_tong_quan": pm["mo_ta"],
            "cac_chuyen_nganh_dao_tao": "Áp dụng cho mọi sinh viên và học viên của trường.",
            "co_hoi_nghe_nghiep_chuc_nang": "Hỗ trợ thanh toán nhanh chóng, gạch nợ tức thời 24/7.",
            "chi_tiet_hoc_phi_hoac_huong_dan": pm["chi_tiet"],
            "dia_diem_phong_lam_viec": "Phòng Kế hoạch - Tài chính (Tầng 1 Nhà A, DUE)",
            "so_dien_thoai_hotline": "0236 3836 172",
            "email_lien_he": "khtc@due.edu.vn",
            "link_fanpage_messenger": "https://epayment.due.udn.vn | https://m.me/FaceDue",
            "cau_hoi_mau_cho_chatbot": pm["prompts"]
        })
        current_id += 1

    # 7. CÂU HỎI THƯỜNG GẶP FAQ (TỪ DATABASE VÀ TUYỂN SINH MỞ RỘNG)
    faqs = CauHoiHocPhi.objects.all().order_by('order')
    for f in faqs:
        records.append({
            "id": f"KB-FAQ-{current_id:03d}",
            "loai_thong_tin": "Câu Hỏi Thường Gặp (FAQ)",
            "ten_chu_de": f.question,
            "khoa_don_vi_quan_ly": "Ban Tư vấn Tuyển sinh & Hỗ trợ sinh viên DUE",
            "ma_dinh_danh_hoac_ma_nganh": "faq-tuyen-sinh",
            "khau_hieu_dinh_huong": "Giải đáp thắc mắc tuyển sinh & học phí 24/7",
            "mo_ta_tong_quan": f"Câu hỏi giải đáp: {f.question}",
            "cac_chuyen_nganh_dao_tao": "Áp dụng cho mọi thí sinh và tân sinh viên.",
            "co_hoi_nghe_nghiep_chuc_nang": "Giải tỏa băn khoăn cho phụ huynh và học sinh chuẩn bị xét tuyển vào DUE.",
            "chi_tiet_hoc_phi_hoac_huong_dan": f.answer,
            "dia_diem_phong_lam_viec": "Tổ Tư vấn Tuyển sinh - Trường ĐH Kinh tế, ĐH Đà Nẵng",
            "so_dien_thoai_hotline": "0236 3950 115 - 0236 3836 169",
            "email_lien_he": "tuyensinh@due.edu.vn",
            "link_fanpage_messenger": "https://www.facebook.com/FaceDue | https://m.me/FaceDue",
            "cau_hoi_mau_cho_chatbot": f"{f.question} | Giải đáp thắc mắc: {f.question}"
        })
        current_id += 1

    return records

def export_to_csv():
    records = build_dataset()
    headers = [
        "id",
        "loai_thong_tin",
        "ten_chu_de",
        "khoa_don_vi_quan_ly",
        "ma_dinh_danh_hoac_ma_nganh",
        "khau_hieu_dinh_huong",
        "mo_ta_tong_quan",
        "cac_chuyen_nganh_dao_tao",
        "co_hoi_nghe_nghiep_chuc_nang",
        "chi_tiet_hoc_phi_hoac_huong_dan",
        "dia_diem_phong_lam_viec",
        "so_dien_thoai_hotline",
        "email_lien_he",
        "link_fanpage_messenger",
        "cau_hoi_mau_cho_chatbot"
    ]

    out_paths = [
        r"e:\CongThongTinTuyenSinhDUE\du_lieu_tuyen_sinh_due_cho_chatbot_ai.csv",
        r"e:\CongThongTinTuyenSinhDUE\CongthongtintuyensinhDUE\du_lieu_tuyen_sinh_due_cho_chatbot_ai.csv"
    ]

    for p in out_paths:
        with open(p, mode='w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for r in records:
                writer.writerow(r)
        print(f"Exported successfully {len(records)} records to: {p}")

if __name__ == '__main__':
    export_to_csv()
