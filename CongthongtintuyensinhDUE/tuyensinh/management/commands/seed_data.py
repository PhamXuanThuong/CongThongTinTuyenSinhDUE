from django.core.management.base import BaseCommand
from tuyensinh.models import KhoaPhongBan, ChuyenNganh, BangHocPhi, CauHoiHocPhi, ChinhSachHocBong

class Command(BaseCommand):
    help = 'Khởi tạo dữ liệu mẫu cho Khoa, Phòng Ban, Học Phí và FAQ'

    def handle(self, *args, **kwargs):
        self.stdout.write("Bat dau nap du lieu Khoa, Phong Ban, Hoc Phi...")

        # 1. BẢNG HỌC PHÍ
        tuition_list = [
            {
                "nhom": "Cử nhân chính quy, Tiêu chuẩn",
                "slug": "tieu-chuan",
                "nam_hoc_1": 29.50,
                "nam_hoc_2": 31.50,
                "nam_hoc_3": 33.50,
                "nam_hoc_4": 35.50,
                "order": 1
            },
            {
                "nhom": "Cử nhân chính quy tài năng, Toàn phần tiếng Anh",
                "slug": "tai-nang",
                "nam_hoc_1": 65.00,
                "nam_hoc_2": 70.00,
                "nam_hoc_3": 75.00,
                "nam_hoc_4": 80.00,
                "order": 2
            },
            {
                "nhom": "Cử nhân chính quy, Toàn phần tiếng Anh",
                "slug": "toan-phan-ta",
                "nam_hoc_1": 43.00,
                "nam_hoc_2": 47.00,
                "nam_hoc_3": 51.00,
                "nam_hoc_4": 55.00,
                "order": 3
            },
            {
                "nhom": "Cử nhân chính quy, Bán phần tiếng Anh",
                "slug": "ban-phan-ta",
                "nam_hoc_1": 36.50,
                "nam_hoc_2": 39.50,
                "nam_hoc_3": 42.50,
                "nam_hoc_4": 45.50,
                "order": 4
            },
        ]
        for t in tuition_list:
            BangHocPhi.objects.update_or_create(
                slug=t["slug"],
                defaults={
                    "nhom": t["nhom"],
                    "nam_hoc_1": t["nam_hoc_1"],
                    "nam_hoc_2": t["nam_hoc_2"],
                    "nam_hoc_3": t["nam_hoc_3"],
                    "nam_hoc_4": t["nam_hoc_4"],
                    "order": t["order"],
                    "is_active": True
                }
            )
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(tuition_list)} tuition rows."))

        # 2. CÂU HỎI THƯỜNG GẶP (FAQ)
        faqs = [
            {
                "question": "Học phí được đóng theo năm hay theo từng học kỳ?",
                "answer": "Học phí tại DUE được thu theo từng học kỳ dựa trên số lượng tín chỉ thực tế sinh viên đăng ký học trong kỳ đó. Một năm học thông thường có 2 học kỳ chính (Kỳ 1 và Kỳ 2), và 1 học kỳ hè phụ (tự nguyện).",
                "order": 1
            },
            {
                "question": "Lộ trình học phí các năm tiếp theo có tăng không?",
                "answer": "Mức tăng học phí qua các năm học được Nhà trường công khai minh bạch ngay từ đầu khóa học (như bảng niêm yết ở trên) và luôn tuân thủ chặt chẽ theo khung trần học phí do Chính phủ quy định đối với cơ sở giáo dục đại học tự chủ.",
                "order": 2
            },
            {
                "question": "Sinh viên gặp khó khăn đột xuất có được xin gia hạn đóng học phí?",
                "answer": "Có. Sinh viên có thể nộp đơn xin gia hạn nộp học phí tại Phòng Công tác sinh viên (Tổ 1 cửa) để được Nhà trường xem xét gia hạn thời gian nộp hoặc hỗ trợ vay vốn, không làm gián đoạn việc đăng ký môn học và thi cử.",
                "order": 3
            },
            {
                "question": "Nhà trường có các gói học bổng nào hỗ trợ học phí không?",
                "answer": "DUE trao tặng quỹ học bổng hàng năm lên tới 25 tỷ đồng: Miễn 100% học phí cho Thủ khoa/Á khoa, học bổng Khuyến khích học tập theo từng kỳ (loại Xuất sắc, Giỏi, Khá) và hàng trăm suất học bổng từ các tập đoàn doanh nghiệp đối tác.",
                "order": 4
            }
        ]
        for f in faqs:
            CauHoiHocPhi.objects.update_or_create(
                question=f["question"],
                defaults={
                    "answer": f["answer"],
                    "order": f["order"],
                    "is_active": True
                }
            )
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(faqs)} FAQ items."))

        # 3. KHOA & PHÒNG BAN
        items_data = [
            # KHOA ĐÀO TẠO
            {
                "code": "khoa-marketing",
                "name": "Khoa Marketing",
                "category": "khoa",
                "tagline": "Sáng tạo không giới hạn - Dẫn lối thương hiệu tương lai (Chuẩn AUN-QA)",
                "color": "bg-red-500",
                "icon": "campaign",
                "fanpage_url": "https://www.facebook.com/due.marketing",
                "messenger_url": "https://m.me/due.marketing",
                "description": "Khoa Marketing - Trường Đại học Kinh tế, ĐH Đà Nẵng là cái nôi đào tạo chuyên gia Marketing hàng đầu miền Trung và cả nước. Đội ngũ giảng viên 100% có trình độ Thạc sĩ, Tiến sĩ tốt nghiệp tại các trường đại học uy tín trong nước và quốc tế.",
                "careers_or_functions": "Chuyên viên Digital Marketing, Quản lý nhãn hàng (Brand Manager), Chuyên viên truyền thông & PR, Chuyên gia phân tích thị trường tại các tập đoàn Unilever, Shopee, TikTok, Agency quảng cáo hàng đầu.",
                "location": "Tầng 3, Nhà E, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3950 115",
                "email": "marketing@due.edu.vn",
                "order": 1,
                "majors": [
                    {"name": "Marketing Số (Digital Marketing)", "note": "Mã ngành: 7340115_01"},
                    {"name": "Truyền thông Marketing tích hợp (IMC)", "note": "Mã ngành: 7340115_02"},
                    {"name": "Quản trị Thương hiệu", "note": "Mã ngành: 7340115_03"},
                    {"name": "Quản trị Bán hàng & Phân phối", "note": "Mã ngành: 7340115_04"}
                ]
            },
            {
                "code": "khoa-ngan-hang",
                "name": "Khoa Ngân hàng",
                "category": "khoa",
                "tagline": "Vững chuyên môn, làm chủ Công nghệ Tài chính Ngân hàng số",
                "color": "bg-blue-500",
                "icon": "account_balance",
                "fanpage_url": "https://www.facebook.com/khoanganhang.due",
                "messenger_url": "https://m.me/khoanganhang.due",
                "description": "Khoa Ngân hàng có bề dày truyền thống đào tạo nguồn nhân lực chất lượng cao cho hệ thống ngân hàng thương mại, các định chế tài chính, bảo hiểm và quỹ đầu tư trong và ngoài nước.",
                "careers_or_functions": "Chuyên viên Tín dụng, Quản lý rủi ro, Phân tích dữ liệu Fintech, Giao dịch viên tại Vietcombank, BIDV, Techcombank, MB Bank và các công ty chứng khoán quốc tế.",
                "location": "Tầng 2, Nhà F, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3847 486",
                "email": "nganhang@due.edu.vn",
                "order": 2,
                "majors": [
                    {"name": "Tài chính - Ngân hàng (Chính quy)", "note": "Mã ngành: 7340201"},
                    {"name": "Công nghệ Tài chính (Fintech)", "note": "Chương trình tiên tiến & CLC"},
                    {"name": "Thẩm định giá & Kinh doanh Bất động sản", "note": "Chuyên ngành thực chiến"}
                ]
            },
            {
                "code": "khoa-qtkd",
                "name": "Khoa Quản trị kinh doanh",
                "category": "khoa",
                "tagline": "Khởi nghiệp - Bản lĩnh - Lãnh đạo tương lai (Chuẩn Quốc tế AUN-QA)",
                "color": "bg-green-600",
                "icon": "corporate_fare",
                "fanpage_url": "https://www.facebook.com/due.qtkd",
                "messenger_url": "https://m.me/due.qtkd",
                "description": "Khoa Quản trị Kinh doanh là một trong những khoa thành lập sớm nhất của trường, tiên phong trong đổi mới phương pháp giảng dạy lấy người học làm trung tâm và đào tạo tinh thần doanh chủ.",
                "careers_or_functions": "Giám đốc vận hành, Quản trị nhân sự, Chuyên viên tư vấn quản trị chiến lược, Nhà sáng lập doanh nghiệp/Startup, Quản lý dự án tại các tập đoàn kinh tế hàng đầu.",
                "location": "Tầng 4, Nhà E, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3836 414",
                "email": "qtkd@due.edu.vn",
                "order": 3,
                "majors": [
                    {"name": "Quản trị kinh doanh tổng hợp", "note": "Mã ngành: 7340101"},
                    {"name": "Quản trị nguồn nhân lực", "note": "Mã ngành: 7340101_02"},
                    {"name": "Quản trị chuỗi cung ứng & Logistics", "note": "Đạt chuẩn AUN-QA"}
                ]
            },
            {
                "code": "khoa-tai-chinh",
                "name": "Khoa Tài chính",
                "category": "khoa",
                "tagline": "Chuyên sâu tài chính công, tài chính doanh nghiệp và đầu tư thông minh",
                "color": "bg-purple-600",
                "icon": "payments",
                "fanpage_url": "https://www.facebook.com/khoataichinhdue",
                "messenger_url": "https://m.me/khoataichinhdue",
                "description": "Khoa Tài chính trang bị nền tảng lý thuyết và thực tiễn vững chắc về quản trị tài chính doanh nghiệp, thị trường vốn, thuế và kiểm soát rủi ro tài chính hiện đại.",
                "careers_or_functions": "Giám đốc tài chính (CFO), Chuyên viên phân tích đầu tư, Chuyên viên hoạch định thuế, Kiểm soát viên tài chính tại các tập đoàn lớn, công ty kiểm toán và cơ quan thuế nhà nước.",
                "location": "Tầng 3, Nhà E, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3950 112",
                "email": "taichinh@due.edu.vn",
                "order": 4,
                "majors": [
                    {"name": "Tài chính doanh nghiệp", "note": "Mã ngành: 7340201_TC"},
                    {"name": "Tài chính công & Thuế", "note": "Chuyên ngành trọng điểm"},
                    {"name": "Đầu tư tài chính & Chứng khoán", "note": "Đào tạo thực hành tại Sàn ảo DUE"}
                ]
            },
            {
                "code": "khoa-thong-ke-tin-hoc",
                "name": "Khoa Thống kê - Tin học",
                "category": "khoa",
                "tagline": "Khai phá dữ liệu - Kiến tạo công nghệ - Quyết định đột phá",
                "color": "bg-orange-500",
                "icon": "query_stats",
                "fanpage_url": "https://www.facebook.com/thongketinhoc.due",
                "messenger_url": "https://m.me/thongketinhoc.due",
                "description": "Đón đầu kỷ nguyên Chuyển đổi số và AI, Khoa Thống kê - Tin học đào tạo những chuyên gia có khả năng phân tích lượng hóa, khai phá dữ liệu lớn (Big Data) và phát triển giải pháp phần mềm thông minh.",
                "careers_or_functions": "Kỹ sư phân tích dữ liệu (Data Analyst/Data Scientist), Lập trình viên hệ thống quản lý, Quản trị cơ sở dữ liệu, Chuyên gia Business Analyst (BA) tại FPT Software, Enclave, Viettel, VNPT.",
                "location": "Tầng 5, Nhà H, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3847 888",
                "email": "tkth@due.edu.vn",
                "order": 5,
                "majors": [
                    {"name": "Khoa học dữ liệu (Data Science)", "note": "Mã ngành: 7480109"},
                    {"name": "Hệ thống thông tin quản lý (MIS)", "note": "Đạt chuẩn AUN-QA"},
                    {"name": "Thống kê kinh tế - xã hội", "note": "Mã ngành: 7310107"}
                ]
            },
            {
                "code": "khoa-tmdt",
                "name": "Khoa Thương mại điện tử",
                "category": "khoa",
                "tagline": "Tiên phong nền kinh tế số - Kết nối giao thương toàn cầu",
                "color": "bg-teal-600",
                "icon": "storefront",
                "fanpage_url": "https://www.facebook.com/khoatmdt.due",
                "messenger_url": "https://m.me/khoatmdt.due",
                "description": "Khoa Thương mại Điện tử là đơn vị đào tạo chuyên sâu về kinh doanh trên nền tảng số, thanh toán điện tử, vận hành sàn TMĐT và tối ưu hóa giải pháp bán hàng đa kênh Omni-channel.",
                "careers_or_functions": "Trưởng phòng TMĐT, Chuyên viên tối ưu gian hàng trực tuyến, Chuyên viên vận hành sàn TMĐT, Quản lý chuỗi bán lẻ số tại Shopee, TikTok Shop, Tiki, Lazada, các chuỗi siêu thị bán lẻ.",
                "location": "Tầng 4, Nhà H, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3950 119",
                "email": "tmdt@due.edu.vn",
                "order": 6,
                "majors": [
                    {"name": "Thương mại điện tử", "note": "Mã ngành: 7340122"},
                    {"name": "Kinh doanh số (Digital Business)", "note": "Chương trình cử nhân hội nhập"},
                    {"name": "Quản trị sàn giao dịch điện tử", "note": "Thực hành cùng Amazon & Lazada"}
                ]
            },
            {
                "code": "khoa-du-lich",
                "name": "Khoa Du lịch",
                "category": "khoa",
                "tagline": "Chuyên nghiệp - Đẳng cấp - Dẫn dắt ngành dịch vụ hiếu khách quốc tế",
                "color": "bg-pink-500",
                "icon": "hotel",
                "fanpage_url": "https://www.facebook.com/khoadulichdue",
                "messenger_url": "https://m.me/khoadulichdue",
                "description": "Nằm tại trung tâm du lịch hàng đầu cả nước là TP. Đà Nẵng, Khoa Du lịch sở hữu mối liên kết chặt chẽ với hàng chục khu nghỉ dưỡng 5 sao, chuỗi khách sạn quốc tế như InterContinental, Marriott, Vinpearl.",
                "careers_or_functions": "Giám đốc khách sạn/Resort, Quản lý tiền sảnh (Front Office Manager), Quản lý điều hành Tour quốc tế, Chuyên viên tổ chức sự kiện chuyên nghiệp tại các thương hiệu du lịch hàng đầu.",
                "location": "Tầng 2, Nhà E, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3836 179",
                "email": "dulich@due.edu.vn",
                "order": 7,
                "majors": [
                    {"name": "Quản trị dịch vụ du lịch và lữ hành", "note": "Mã ngành: 7810103"},
                    {"name": "Quản trị khách sạn", "note": "Mã ngành: 7810201 (Chuẩn AUN-QA)"},
                    {"name": "Quản trị sự kiện và lễ hội", "note": "Chuyên ngành năng động"}
                ]
            },
            {
                "code": "khoa-ke-toan",
                "name": "Khoa Kế toán",
                "category": "khoa",
                "tagline": "Minh bạch tài chính - Chuẩn mực nghề nghiệp quốc tế (ACCA, CPA)",
                "color": "bg-red-600",
                "icon": "calculate",
                "fanpage_url": "https://www.facebook.com/khoaketoandue",
                "messenger_url": "https://m.me/khoaketoandue",
                "description": "Khoa Kế toán DUE là trung tâm đào tạo kế toán - kiểm toán uy tín nhất khu vực, tích hợp chứng chỉ nghề nghiệp quốc tế ACCA (Anh Quốc) và CPA Australia trực tiếp vào chương trình đào tạo.",
                "careers_or_functions": "Kiểm toán viên tại nhóm Big 4 (PwC, EY, KPMG, Deloitte), Kế toán trưởng, Giám đốc kiểm soát nội bộ tại các ngân hàng, doanh nghiệp có vốn đầu tư nước ngoài (FDI).",
                "location": "Tầng 3, Nhà F, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3950 114",
                "email": "ketoan@due.edu.vn",
                "order": 8,
                "majors": [
                    {"name": "Kế toán tổng hợp", "note": "Mã ngành: 7340301 (AUN-QA)"},
                    {"name": "Kiểm toán", "note": "Mã ngành: 7340302"},
                    {"name": "Kế toán công và kiểm soát nội bộ", "note": "Chuẩn mực quốc tế"}
                ]
            },
            {
                "code": "khoa-kdqt",
                "name": "Khoa Kinh doanh quốc tế",
                "category": "khoa",
                "tagline": "Vươn tầm quốc tế - Làm chủ chuỗi cung ứng toàn cầu",
                "color": "bg-blue-600",
                "icon": "public",
                "fanpage_url": "https://www.facebook.com/due.kdqt",
                "messenger_url": "https://m.me/due.kdqt",
                "description": "Khoa Kinh doanh Quốc tế đào tạo cử nhân có tư duy toàn cầu, tinh thông nghiệp vụ xuất nhập khẩu, thanh toán quốc tế và chuỗi cung ứng toàn cầu trong kỷ nguyên hội nhập FTA.",
                "careers_or_functions": "Chuyên viên Logistics quốc tế, Chuyên viên Forwarder, Quản lý thu mua toàn cầu, Chuyên viên chứng từ thanh toán quốc tế tại cảng biển, hãng tàu Maersk, MSC, các tập đoàn đa quốc gia.",
                "location": "Tầng 4, Nhà F, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3950 116",
                "email": "kdqt@due.edu.vn",
                "order": 9,
                "majors": [
                    {"name": "Kinh doanh quốc tế", "note": "Mã ngành: 7340120 (Chuẩn AUN-QA)"},
                    {"name": "Logistics và Quản lý Chuỗi cung ứng", "note": "Ngành học điểm chuẩn xuất sắc"},
                    {"name": "Thương mại quốc tế", "note": "Chương trình định hướng hội nhập"}
                ]
            },
            {
                "code": "khoa-kinh-te",
                "name": "Khoa Kinh tế",
                "category": "khoa",
                "tagline": "Phân tích sắc bén - Hoạch định chính sách - Kiến tạo thịnh vượng",
                "color": "bg-green-700",
                "icon": "trending_up",
                "fanpage_url": "https://www.facebook.com/due.khoakinhte",
                "messenger_url": "https://m.me/due.khoakinhte",
                "description": "Khoa Kinh tế đào tạo những nhà kinh tế có tầm nhìn chiến lược, khả năng phân tích kinh tế vĩ mô và vi mô, hoạch định chính sách phát triển kinh tế vùng và quản lý đô thị hiện đại.",
                "careers_or_functions": "Chuyên viên phân tích vĩ mô tại các quỹ đầu tư, ngân hàng, Viện nghiên cứu kinh tế, Sở Kế hoạch & Đầu tư, Ban quản lý dự án công và các tổ chức phi chính phủ (NGOs).",
                "location": "Tầng 5, Nhà E, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3847 487",
                "email": "kinhte@due.edu.vn",
                "order": 10,
                "majors": [
                    {"name": "Kinh tế phát triển", "note": "Mã ngành: 7310105"},
                    {"name": "Kinh tế đầu tư", "note": "Chuyên ngành trọng điểm"},
                    {"name": "Kinh tế và Quản lý công", "note": "Đào tạo lãnh đạo quản lý"}
                ]
            },
            {
                "code": "khoa-luat",
                "name": "Khoa Luật",
                "category": "khoa",
                "tagline": "Công lý - Bản lĩnh - Đồng hành cùng cộng đồng doanh nghiệp",
                "color": "bg-purple-700",
                "icon": "gavel",
                "fanpage_url": "https://www.facebook.com/due.khoaluat",
                "messenger_url": "https://m.me/due.khoaluat",
                "description": "Khoa Luật trường Đại học Kinh tế đào tạo cử nhân Luật với thế mạnh vượt trội về Pháp luật kinh doanh, Thương mại quốc tế, Trọng tài thương mại và Sở hữu trí tuệ.",
                "careers_or_functions": "Luật sư tư vấn doanh nghiệp, Pháp chế nội bộ (In-house Counsel), Thẩm phán, Kiểm sát viên, Thư ký tòa án, Trọng tài viên thương mại tại các hãng luật hàng đầu.",
                "location": "Tầng 2, Nhà H, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3950 118",
                "email": "luat@due.edu.vn",
                "order": 11,
                "majors": [
                    {"name": "Luật kinh tế", "note": "Mã ngành: 7380107"},
                    {"name": "Luật học (Chung)", "note": "Mã ngành: 7380101"},
                    {"name": "Pháp luật thương mại quốc tế", "note": "Chuyên sâu hội nhập kinh tế"}
                ]
            },
            {
                "code": "khoa-llct",
                "name": "Khoa Lý luận chính trị",
                "category": "khoa",
                "tagline": "Nền tảng tư duy biện chứng - Nhân văn - Bản lĩnh công dân toàn cầu",
                "color": "bg-orange-600",
                "icon": "menu_book",
                "fanpage_url": "https://www.facebook.com/FaceDue",
                "messenger_url": "https://m.me/FaceDue",
                "description": "Khoa Lý luận chính trị chịu trách nhiệm giảng dạy các môn khoa học xã hội và nhân văn nền tảng, bồi dưỡng tư tưởng chính trị, đạo đức và thế giới quan khoa học cho sinh viên toàn trường.",
                "careers_or_functions": "Trang bị phương pháp luận tư duy logic, phản biện và định hướng nghề nghiệp vững vàng cho mọi ngành nghề quản trị, kinh doanh và xã hội.",
                "location": "Tầng 5, Nhà H, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3836 180",
                "email": "llct@due.edu.vn",
                "order": 12,
                "majors": [
                    {"name": "Giảng dạy khối kiến thức Đại cương", "note": "Toàn bộ sinh viên DUE"},
                    {"name": "Nghiên cứu khoa học Xã hội & Nhân văn", "note": "Đề tài cấp Bộ & Quốc tế"}
                ]
            },

            # PHÒNG BAN CHỨC NĂNG
            {
                "code": "pb-ctsv",
                "name": "Phòng Công tác sinh viên, Quan hệ Doanh nghiệp và Truyền thông",
                "category": "phong_ban",
                "tagline": "Tận tâm vì sinh viên - Cầu nối vững chắc với Doanh nghiệp",
                "color": "bg-sky-500",
                "icon": "support_agent",
                "fanpage_url": "https://www.facebook.com/ctsv.due.udn.vn",
                "messenger_url": "https://m.me/ctsv.due.udn.vn",
                "description": "Đầu mối tiếp nhận, giải quyết chế độ chính sách, học bổng sinh viên, tư vấn tâm lý, tổ chức ngày hội việc làm (Job Fair) và điều phối công tác truyền thông tuyển sinh của nhà trường.",
                "careers_or_functions": "Đơn vị cung cấp các kỹ năng mềm, cơ hội thực tập và kết nối việc làm với hơn 500 đối tác doanh nghiệp lớn cho toàn thể sinh viên trường.",
                "location": "Phòng 102, Nhà Hiệu bộ, 71 Ngũ Hành Sơn, Đà Nẵng",
                "phone": "0236 3950 110",
                "email": "ctsv@due.edu.vn",
                "order": 13,
                "majors": [
                    {"name": "Xét cấp học bổng khuyến khích học tập & học bổng doanh nghiệp", "note": "Hàng kỳ"},
                    {"name": "Tổ chức DUE Career Fair & Ngày hội tuyển dụng", "note": "Quy mô 5000+ sinh viên"},
                    {"name": "Hỗ trợ thủ tục tạm hoãn nghĩa vụ quân sự, thẻ SV", "note": "Một cửa hành chính"}
                ]
            },
            {
                "code": "pb-dao-tao",
                "name": "Phòng Đào tạo",
                "category": "phong_ban",
                "tagline": "Quản lý đào tạo chuẩn mực, linh hoạt theo hệ thống tín chỉ tiên tiến",
                "color": "bg-indigo-600",
                "icon": "history_edu",
                "fanpage_url": "https://www.facebook.com/tuyensinhdue",
                "messenger_url": "https://m.me/tuyensinhdue",
                "description": "Đơn vị tham mưu cho Ban Giám hiệu về kế hoạch đào tạo, chương trình đào tạo đại học, quản lý kết quả học tập, đăng ký học phần và cấp phát văn bằng cử nhân.",
                "careers_or_functions": "Hỗ trợ tối đa lộ trình học tập, chuyển đổi tín chỉ và học văn bằng 2, song bằng dành cho sinh viên xuất sắc.",
                "location": "Tầng 1, Nhà Hiệu bộ, 71 Ngũ Hành Sơn, Đà Nẵng",
                "phone": "0236 3836 169",
                "email": "daotao@due.edu.vn",
                "order": 14,
                "majors": [
                    {"name": "Quản lý tuyển sinh Đại học chính quy", "note": "Cổng tuyển sinh trực tuyến"},
                    {"name": "Điều phối lịch học, thi và đăng ký tín chỉ", "note": "Hệ thống Portal sinh viên"},
                    {"name": "Xét tốt nghiệp và cấp bằng chuẩn AUN-QA", "note": "Chu kỳ 4 năm/khoá"}
                ]
            },
            {
                "code": "pb-tchc",
                "name": "Phòng Tổ chức - Hành chính",
                "category": "phong_ban",
                "tagline": "Kỷ cương - Chuyên nghiệp - Phục vụ hiệu quả",
                "color": "bg-fuchsia-600",
                "icon": "badge",
                "fanpage_url": "https://www.facebook.com/FaceDue",
                "messenger_url": "https://m.me/FaceDue",
                "description": "Tham mưu cho Hiệu trưởng về công tác quy hoạch, tuyển dụng, bồi dưỡng đội ngũ cán bộ giảng viên; quản trị văn thư lưu trữ và điều hành hành chính văn phòng.",
                "careers_or_functions": "Xây dựng môi trường giáo dục đại học nhân văn, kỷ cương và chuyên nghiệp cao.",
                "location": "Tầng 2, Nhà Hiệu bộ, 71 Ngũ Hành Sơn, Đà Nẵng",
                "phone": "0236 3836 168",
                "email": "tchc@due.edu.vn",
                "order": 15,
                "majors": [
                    {"name": "Quản lý nhân sự và chế độ giảng viên", "note": "100% cán bộ đạt chuẩn"},
                    {"name": "Công tác văn thư lưu trữ, chứng thực văn bản", "note": "Hệ thống E-Office"}
                ]
            },
            {
                "code": "pb-khhtqt",
                "name": "Phòng Khoa học và Hợp tác Quốc tế",
                "category": "phong_ban",
                "tagline": "Thúc đẩy nghiên cứu khoa học đỉnh cao & Hội nhập học thuật toàn cầu",
                "color": "bg-emerald-600",
                "icon": "biotech",
                "fanpage_url": "https://www.facebook.com/FaceDue",
                "messenger_url": "https://m.me/FaceDue",
                "description": "Quản lý các đề tài nghiên cứu khoa học sinh viên và giảng viên, tổ chức các hội thảo quốc tế lớn và kết nối chương trình trao đổi sinh viên quốc tế (Erasmus+, chuyển tiếp 2+2).",
                "careers_or_functions": "Tạo cơ hội cho sinh viên tiếp cận các học bổng du học, tham gia hội nghị quốc tế và xuất bản bài báo học thuật uy tín.",
                "location": "Tầng 3, Nhà Hiệu bộ, 71 Ngũ Hành Sơn, Đà Nẵng",
                "phone": "0236 3950 113",
                "email": "khhtqt@due.edu.vn",
                "order": 16,
                "majors": [
                    {"name": "Phong trào Sinh viên Nghiên cứu Khoa học", "note": "Nhiều giải thưởng cấp Bộ & Quốc gia"},
                    {"name": "Chương trình trao đổi sinh viên quốc tế", "note": "Pháp, Anh, Mỹ, Nhật Bản, Hàn Quốc"}
                ]
            },
            {
                "code": "pb-qlcl",
                "name": "Phòng Quản lý chất lượng",
                "category": "phong_ban",
                "tagline": "Cam kết chất lượng - Chuẩn hóa quy trình theo chuẩn mực quốc tế",
                "color": "bg-rose-500",
                "icon": "fact_check",
                "fanpage_url": "https://www.facebook.com/FaceDue",
                "messenger_url": "https://m.me/FaceDue",
                "description": "Phụ trách kiểm định chất lượng cơ sở giáo dục, kiểm định chương trình đào tạo theo chuẩn AUN-QA và Bộ GD&ĐT, đồng thời tổ chức thi và khảo sát sự hài lòng của người học.",
                "careers_or_functions": "Đảm bảo tấm bằng tốt nghiệp của sinh viên DUE có giá trị cạnh tranh cao trên thị trường lao động trong nước và quốc tế.",
                "location": "Tầng 2, Nhà F, 71 Ngũ Hành Sơn, Đà Nẵng",
                "phone": "0236 3950 117",
                "email": "qlcl@due.edu.vn",
                "order": 17,
                "majors": [
                    {"name": "Kiểm định chất lượng AUN-QA & FIBAA", "note": "Tiêu chuẩn quốc tế"},
                    {"name": "Tổ chức và giám sát kỳ thi an toàn, nghiêm túc", "note": "Khách quan, minh bạch"}
                ]
            },
            {
                "code": "pb-khtc",
                "name": "Phòng Kế hoạch - Tài chính",
                "category": "phong_ban",
                "tagline": "Quản lý tài chính minh bạch, hỗ trợ tối đa học phí sinh viên",
                "color": "bg-amber-600",
                "icon": "receipt_long",
                "fanpage_url": "https://www.facebook.com/FaceDue",
                "messenger_url": "https://m.me/FaceDue",
                "description": "Thực hiện thu học phí, giải ngân học bổng, quản lý nguồn kinh phí hoạt động và phân bổ ngân sách đầu tư cơ sở vật chất phục vụ sinh viên học tập.",
                "careers_or_functions": "Đơn vị đồng hành đảm bảo quyền lợi tài chính và các gói hỗ trợ tín dụng học tập cho sinh viên hoàn cảnh khó khăn.",
                "location": "Tầng 1, Nhà Hiệu bộ, 71 Ngũ Hành Sơn, Đà Nẵng",
                "phone": "0236 3847 485",
                "email": "khtc@due.edu.vn",
                "order": 18,
                "majors": [
                    {"name": "Thanh toán học phí trực tuyến liên ngân hàng", "note": "Hỗ trợ 24/7 qua App ngân hàng"},
                    {"name": "Chi trả chế độ học bổng, miễn giảm học phí", "note": "Nhanh chóng, chính xác"}
                ]
            },
            {
                "code": "pb-csvc",
                "name": "Phòng Cơ sở vật chất",
                "category": "phong_ban",
                "tagline": "Không gian học tập hiện đại - Giảng đường thông minh chuẩn quốc tế",
                "color": "bg-cyan-600",
                "icon": "domain",
                "fanpage_url": "https://www.facebook.com/FaceDue",
                "messenger_url": "https://m.me/FaceDue",
                "description": "Quản lý và vận hành hệ thống giảng đường 100% máy lạnh, máy chiếu thông minh, phòng máy tính cấu hình cao, khuôn viên cây xanh và ký túc xá sinh viên hiện đại.",
                "careers_or_functions": "Mang lại môi trường học tập, sinh hoạt tiện nghi, năng động và an toàn tuyệt đối cho người học.",
                "location": "Tầng 1, Nhà G, 71 Ngũ Hành Sơn, Đà Nẵng",
                "phone": "0236 3836 170",
                "email": "csvc@due.edu.vn",
                "order": 19,
                "majors": [
                    {"name": "Giảng đường thông minh (Smart Classrooms)", "note": "Trang bị đầy đủ âm thanh, ánh sáng hiện đại"},
                    {"name": "Khu ký túc xá và khu phức hợp thể thao", "note": "Sân bóng đá, bóng rổ, tennis"}
                ]
            },
            {
                "code": "pb-ttshl",
                "name": "Trung tâm Số và Học liệu",
                "category": "phong_ban",
                "tagline": "Kho tàng tri thức vô tận - Không gian tự học và sáng tạo lý tưởng",
                "color": "bg-sky-600",
                "icon": "local_library",
                "fanpage_url": "https://www.facebook.com/FaceDue",
                "messenger_url": "https://m.me/FaceDue",
                "description": "Thư viện số DUE sở hữu hàng triệu đầu sách kinh tế, tạp chí học thuật quốc tế (Scopus, ScienceDirect, Springer), cùng không gian tự học máy lạnh, phòng thảo luận nhóm hiện đại.",
                "careers_or_functions": "Điểm đến học tập và nghiên cứu lý tưởng, hỗ trợ đắc lực tài liệu học thuật cho sinh viên suốt 4 năm đại học.",
                "location": "Tòa nhà Thư viện, Trường ĐH Kinh tế - ĐH Đà Nẵng",
                "phone": "0236 3836 182",
                "email": "thuvien@due.edu.vn",
                "order": 20,
                "majors": [
                    {"name": "Thư viện điện tử & Cơ sở dữ liệu quốc tế", "note": "Truy cập từ xa 24/7"},
                    {"name": "Khu vực tự học & Không gian Co-working space", "note": "Miễn phí wifi tốc độ cao"}
                ]
            },
            {
                "code": "pb-ttnnth",
                "name": "Trung tâm Ngoại ngữ - Tin học",
                "category": "phong_ban",
                "tagline": "Chuẩn hóa năng lực Ngoại ngữ & Tin học quốc tế (TOEIC, IELTS, MOS)",
                "color": "bg-indigo-700",
                "icon": "translate",
                "fanpage_url": "https://www.facebook.com/FaceDue",
                "messenger_url": "https://m.me/FaceDue",
                "description": "Đào tạo, luyện thi và tổ chức các kỳ thi cấp chứng chỉ chuẩn đầu ra ngoại ngữ (Tiếng Anh TOEIC/IELTS, Tiếng Nhật, Tiếng Trung) và chứng chỉ Tin học văn phòng quốc tế MOS cho sinh viên.",
                "careers_or_functions": "Giúp 100% sinh viên đáp ứng chuẩn đầu ra tốt nghiệp và tự tin ứng tuyển vào các tập đoàn đa quốc gia đòi hỏi tiếng Anh thành thạo.",
                "location": "Tầng 1, Nhà H, 71 Ngũ Hành Sơn, Đà Nẵng",
                "phone": "0236 3847 488",
                "email": "ttnnth@due.edu.vn",
                "order": 21,
                "majors": [
                    {"name": "Luyện thi chứng chỉ tiếng Anh chuẩn đầu ra TOEIC / IELTS", "note": "Giảng viên chuyên môn cao"},
                    {"name": "Đào tạo và sát hạch Tin học văn phòng quốc tế MOS", "note": "Cấp chứng chỉ của Microsoft"}
                ]
            }
        ]

        for item in items_data:
            majors = item.pop("majors", [])
            obj, created = KhoaPhongBan.objects.update_or_create(
                code=item["code"],
                defaults=item
            )
            # Recreate majors
            obj.majors.all().delete()
            for idx, m in enumerate(majors, 1):
                ChuyenNganh.objects.create(
                    khoa=obj,
                    name=m["name"],
                    note=m.get("note", ""),
                    order=idx
                )

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(items_data)} faculties and departments."))
        self.stdout.write(self.style.SUCCESS("SEED DATA COMPLETED SUCCESSFULLY!"))
