from django.db import models
from django.utils.text import slugify

class TinTuc(models.Model):
    THE_LOAI_CHOICES = [
        ('tuyen_sinh', 'Tuyển sinh'),
        ('workshop', 'Workshop và hướng nghiệp'),
        ('hoc_bong', 'Học bổng và chính sách'),
        ('su_kien', 'Sự kiện và hoạt động'),
    ]

    tieu_de = models.CharField(max_length=255, verbose_name="Tiêu đề bài viết")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug (đường dẫn)")
    the_loai = models.CharField(max_length=50, choices=THE_LOAI_CHOICES, default='tuyen_sinh', verbose_name="Thể loại")
    hinh_anh = models.CharField(max_length=500, blank=True, verbose_name="Đường dẫn hoặc URL ảnh")
    tom_tat = models.TextField(verbose_name="Tóm tắt ngắn")
    noi_dung = models.TextField(blank=True, verbose_name="Nội dung chi tiết")
    ngay_dang = models.DateField(auto_now_add=True, verbose_name="Ngày đăng")
    luot_xem = models.PositiveIntegerField(default=0, verbose_name="Lượt xem")
    noi_bat = models.BooleanField(default=True, verbose_name="Hiển thị trang chủ")

    class Meta:
        db_table = 'admissions_news'
        verbose_name = "Bản tin tuyển sinh và sự kiện"
        verbose_name_plural = "1. Quản lý Tin tức và sự kiện"
        ordering = ['-ngay_dang', '-id']

    def __str__(self):
        return self.tieu_de

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.tieu_de)
        super().save(*args, **kwargs)


class LoaiHinhDaoTao(models.Model):
    LOAI_HINH_CHOICES = [
        ('toan_phan', 'Toàn phần tiếng Anh'),
        ('ban_phan', 'Bán phần tiếng Anh'),
        ('tieu_chuan', 'Chương trình Tiêu chuẩn (DUE-Standard)'),
    ]
    ma_loai_hinh = models.CharField(max_length=50, choices=LOAI_HINH_CHOICES, unique=True, verbose_name="Mã loại hình")
    ten_loai_hinh = models.CharField(max_length=150, verbose_name="Tên loại hình đào tạo")
    mo_ta = models.TextField(verbose_name="Mô tả đặc điểm và ưu thế")
    ngon_ngu = models.CharField(max_length=100, default="Tiếng Việt và tiếng Anh", verbose_name="Ngôn ngữ giảng dạy")
    thoi_gian_dao_tao = models.CharField(max_length=50, default="4 năm (8 học kỳ)", verbose_name="Thời gian đào tạo")
    bang_cap = models.CharField(max_length=150, default="Cử nhân chính quy", verbose_name="Bằng cấp tốt nghiệp")
    icon = models.CharField(max_length=50, default="school", verbose_name="Biểu tượng Material Symbol")
    thu_tu = models.PositiveIntegerField(default=1, verbose_name="Thứ tự hiển thị")

    class Meta:
        db_table = 'admissions_training_type'
        verbose_name = "Loại hình đào tạo"
        verbose_name_plural = "2. Loại hình đào tạo"
        ordering = ['thu_tu']

    def __str__(self):
        return self.ten_loai_hinh


class NganhDaoTao(models.Model):
    ma_nganh = models.CharField(max_length=20, unique=True, verbose_name="Mã ngành/Mã xét tuyển")
    ten_nganh = models.CharField(max_length=150, verbose_name="Tên ngành / Chuyên ngành đào tạo")
    khoa = models.CharField(max_length=100, blank=True, verbose_name="Khoa chuyên môn phụ trách")
    loai_hinh = models.ForeignKey(LoaiHinhDaoTao, on_delete=models.SET_NULL, null=True, blank=True, related_name='nganh_hoc', verbose_name="Loại hình đào tạo chính")
    chi_tieu = models.PositiveIntegerField(default=100, verbose_name="Tổng chỉ tiêu dự kiến 2026")
    chi_tieu_toan_phan = models.PositiveIntegerField(default=0, verbose_name="Chỉ tiêu Toàn phần TA")
    chi_tieu_ban_phan = models.PositiveIntegerField(default=0, verbose_name="Chỉ tiêu Bán phần TA")
    chi_tieu_tieu_chuan = models.PositiveIntegerField(default=0, verbose_name="Chỉ tiêu Tiêu chuẩn")
    to_hop_mon = models.CharField(max_length=100, default="A00, A01, D01, D07, X25, X26", verbose_name="Tổ hợp xét tuyển")
    hoc_phi_du_kien = models.CharField(max_length=100, blank=True, default="Theo quy định Nhà nước", verbose_name="Học phí dự kiến")
    mo_ta = models.TextField(blank=True, verbose_name="Mô tả ngành và cơ hội việc làm")

    class Meta:
        db_table = 'admissions_major'
        verbose_name = "Ngành đào tạo và chỉ tiêu"
        verbose_name_plural = "3. Danh mục Ngành và chỉ tiêu tuyển sinh"
        ordering = ['ma_nganh']

    def __str__(self):
        return f"{self.ma_nganh} - {self.ten_nganh}"


class DiemChuan(models.Model):
    PHUONG_THUC_CHOICES = [
        ('THPT', 'Điểm thi tốt nghiệp THPT'),
        ('HOC_BA', 'Xét học bạ THPT kết hợp'),
        ('DGNL', 'Đánh giá năng lực ĐHQG-HCM'),
        ('XTT', 'Xét tuyển thẳng và ưu tiên'),
    ]

    nganh = models.ForeignKey(NganhDaoTao, on_delete=models.CASCADE, related_name='diem_chuan_cac_nam', verbose_name="Ngành đào tạo")
    nam = models.PositiveIntegerField(verbose_name="Năm tuyển sinh (2025, 2024, 2023, 2022)")
    phuong_thuc = models.CharField(max_length=20, choices=PHUONG_THUC_CHOICES, default='THPT', verbose_name="Phương thức xét tuyển")
    diem_trung_tuyen = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Điểm chuẩn trúng tuyển")
    to_hop_xet_tuyen = models.CharField(max_length=100, blank=True, default="A00, A01, D01, D07", verbose_name="Tổ hợp áp dụng")
    tieu_chi_phu = models.CharField(max_length=255, blank=True, verbose_name="Tiêu chí phụ (nếu có)")
    ghi_chu = models.CharField(max_length=255, blank=True, verbose_name="Ghi chú")

    class Meta:
        db_table = 'admissions_benchmark'
        verbose_name = "Điểm chuẩn theo năm"
        verbose_name_plural = "4. Điểm chuẩn trúng tuyển các năm"
        ordering = ['-nam', 'nganh__ma_nganh', 'phuong_thuc']
        unique_together = ('nganh', 'nam', 'phuong_thuc')

    def __str__(self):
        return f"{self.nganh.ten_nganh} ({self.nam}) - {self.diem_trung_tuyen}đ [{self.get_phuong_thuc_display()}]"


class PhuongThucXetTuyen(models.Model):
    ma_phuong_thuc = models.CharField(max_length=20, unique=True, verbose_name="Mã phương thức (PT1, PT2,...)")
    ten_phuong_thuc = models.CharField(max_length=200, verbose_name="Tên phương thức xét tuyển")
    doi_tuong_ap_dung = models.TextField(verbose_name="Đối tượng và điều kiện áp dụng")
    chuong_trinh_ap_dung = models.CharField(max_length=200, default="Áp dụng các chương trình đào tạo", verbose_name="Chương trình áp dụng")
    nguyen_tac_xet = models.TextField(blank=True, verbose_name="Nguyên tắc xét tuyển và cách tính điểm")
    mau_sac = models.CharField(max_length=30, default="blue", verbose_name="Tone màu đại diện (blue, emerald, orange, amber)")
    thu_tu = models.PositiveIntegerField(default=1, verbose_name="Thứ tự hiển thị")

    class Meta:
        db_table = 'admissions_method'
        verbose_name = "Phương thức xét tuyển"
        verbose_name_plural = "5. Phương thức xét tuyển 2026"
        ordering = ['thu_tu']

    def __str__(self):
        return f"{self.ma_phuong_thuc} - {self.ten_phuong_thuc}"


class CauHoiThuongGap(models.Model):
    PHAN_LOAI_CHOICES = [
        ('GioiThieuChung', 'Tổng quan và giới thiệu'),
        ('LichSuPhatTrien', 'Lịch sử phát triển'),
        ('SuMangTamNhin', 'Sứ mệnh và tầm nhìn'),
        ('PhuongThucXetTuyen', 'Phương thức xét tuyển'),
        ('ChiTieuNganhHoc', 'Chỉ tiêu và ngành học'),
        ('DiemChuan', 'Điểm chuẩn và xét tuyển'),
        ('HocPhiHocBong', 'Học phí và học bổng'),
        ('Khac', 'Thông tin khác'),
    ]

    ma_cau_hoi = models.CharField(max_length=50, unique=True, verbose_name="Mã câu hỏi (ID)")
    chu_de = models.CharField(max_length=150, verbose_name="Chủ đề câu hỏi")
    phan_loai = models.CharField(max_length=50, choices=PHAN_LOAI_CHOICES, default='GioiThieuChung', verbose_name="Phân loại")
    cau_hoi_mau = models.TextField(verbose_name="Các biến thể câu hỏi (cách nhau bởi dấu |)")
    cau_tra_loi = models.TextField(verbose_name="Câu trả lời chi tiết")
    tu_khoa = models.TextField(blank=True, verbose_name="Từ khóa tìm kiếm (search keywords)")
    nguon_tham_khao = models.CharField(max_length=300, blank=True, verbose_name="Nguồn tham khảo chính thức")
    kich_hoat = models.BooleanField(default=True, verbose_name="Kích hoạt trợ lý AI / Chatbot")

    class Meta:
        db_table = 'admissions_faq'
        verbose_name = "Hỏi đáp và tri thức Chatbot"
        verbose_name_plural = "6. Tri thức Chatbot và hỏi đáp tự động"
        ordering = ['id']

    def __str__(self):
        return f"[{self.ma_cau_hoi}] {self.chu_de}"


class TuVanTuyenSinh(models.Model):
    TRANG_THAI_CHOICES = [
        ('cho_xu_ly', 'Chờ xử lý'),
        ('dang_tu_van', 'Đang liên hệ tư vấn'),
        ('da_hoan_thanh', 'Đã tư vấn xong'),
        ('huy', 'Hủy / Không liên lạc được'),
    ]

    ho_ten = models.CharField(max_length=100, verbose_name="Họ và tên thí sinh / phụ huynh")
    so_dien_thoai = models.CharField(max_length=15, verbose_name="Số điện thoại")
    email = models.EmailField(blank=True, verbose_name="Email liên hệ")
    nganh_quan_tam = models.CharField(max_length=150, blank=True, verbose_name="Ngành học quan tâm")
    noi_dung_cau_hoi = models.TextField(verbose_name="Nội dung câu hỏi / cần tư vấn")
    trang_thai = models.CharField(max_length=30, choices=TRANG_THAI_CHOICES, default='cho_xu_ly', verbose_name="Trạng thái xử lý")
    da_tu_van = models.BooleanField(default=False, verbose_name="Đã phản hồi (Legacy)")
    ghi_chu_noi_bo = models.TextField(blank=True, verbose_name="Ghi chú nội bộ ban tư vấn")
    ngay_gui = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian gửi")
    ngay_cap_nhat = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        db_table = 'admissions_counseling_request'
        verbose_name = "Yêu cầu tư vấn tuyển sinh"
        verbose_name_plural = "7. Yêu cầu tư vấn của Thí sinh"
        ordering = ['-ngay_gui']

    def __str__(self):
        return f"{self.ho_ten} ({self.so_dien_thoai}) - {self.get_trang_thai_display()}"


# ========================================================
# CÁC MODEL KHOA, PHÒNG BAN, HỌC PHÍ, HỌC BỔNG (TỪ NHÁNH MAIN)
# ========================================================

class KhoaPhongBan(models.Model):
    CATEGORY_CHOICES = [
        ("khoa", "Khoa Đào Tạo"),
        ("phong_ban", "Phòng Ban Chức Năng / Trung Tâm"),
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Mã định danh (slug)",
        help_text="Ví dụ: khoa-marketing, pb-ctsv",
    )
    name = models.CharField(max_length=200, verbose_name="Tên Khoa / Phòng ban")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="khoa",
        verbose_name="Loại đơn vị",
    )
    tagline = models.CharField(
        max_length=255, blank=True, verbose_name="Khẩu hiệu / Định hướng"
    )
    color = models.CharField(
        max_length=50, default="bg-blue-600", verbose_name="Màu badge/icon (Tailwind)"
    )
    icon = models.CharField(
        max_length=50, default="school", verbose_name="Icon Material Symbols"
    )
    description = models.TextField(verbose_name="Mô tả / Giới thiệu")
    careers_or_functions = models.TextField(
        verbose_name="Cơ hội việc làm / Chức năng chính"
    )
    location = models.CharField(
        max_length=255,
        default="Trường ĐH Kinh tế - ĐH Đà Nẵng",
        verbose_name="Địa điểm phòng làm việc",
    )
    phone = models.CharField(
        max_length=50, blank=True, verbose_name="Số điện thoại liên hệ"
    )
    email = models.CharField(max_length=100, blank=True, verbose_name="Email liên hệ")
    fanpage_url = models.URLField(
        blank=True,
        default="https://www.facebook.com/FaceDue",
        verbose_name="Link Fanpage",
    )
    messenger_url = models.URLField(
        blank=True, default="https://m.me/FaceDue", verbose_name="Link Messenger"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")

    class Meta:
        db_table = 'admissions_faculty_department_legacy'
        verbose_name = "Khoa / Phòng Ban"
        verbose_name_plural = "Danh sách Khoa và phòng Ban"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"

    def to_dict(self):
        """Chuyển thành dict để serialize sang JSON dùng cho popup modal"""
        return {
            "category": self.get_category_display(),
            "title": self.name,
            "tagline": self.tagline,
            "color": self.color,
            "icon": self.icon,
            "fanpage": self.fanpage_url,
            "messenger": self.messenger_url,
            "desc": self.description,
            "majors": [{"name": m.name, "note": m.note} for m in self.majors.all()],
            "careers": self.careers_or_functions,
            "location": self.location,
            "phone": self.phone,
            "email": self.email,
        }


class ChuyenNganh(models.Model):
    khoa = models.ForeignKey(
        KhoaPhongBan,
        on_delete=models.CASCADE,
        related_name="majors",
        verbose_name="Thuộc Khoa",
    )
    name = models.CharField(max_length=200, verbose_name="Tên Ngành / Chuyên ngành")
    note = models.CharField(
        max_length=150, blank=True, verbose_name="Mã ngành hoặc ghi chú"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        db_table = 'admissions_specialization'
        verbose_name = "Chuyên ngành đào tạo"
        verbose_name_plural = "Danh sách Chuyên ngành"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} ({self.khoa.name})"


class BangHocPhi(models.Model):
    nhom = models.CharField(max_length=200, verbose_name="Nhóm chương trình")
    slug = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Mã nhóm",
        help_text="Dùng cho công cụ tính: tieu-chuan, tai-nang, toan-phan-ta, ban-phan-ta",
    )
    nam_hoc_1 = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Năm học 2026 - 2027 (Triệu đồng)"
    )
    nam_hoc_2 = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Năm học 2027 - 2028 (Triệu đồng)"
    )
    nam_hoc_3 = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Năm học 2028 - 2029 (Triệu đồng)"
    )
    nam_hoc_4 = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Năm học 2029 - 2030 (Triệu đồng)"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")

    class Meta:
        db_table = 'admissions_tuition_fee'
        verbose_name = "Mức học phí"
        verbose_name_plural = "Bảng học phí các năm"
        ordering = ["order", "id"]

    def __str__(self):
        return self.nhom


class CauHoiHocPhi(models.Model):
    question = models.CharField(max_length=255, verbose_name="Câu hỏi")
    answer = models.TextField(verbose_name="Câu trả lời")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")

    class Meta:
        db_table = 'admissions_tuition_faq'
        verbose_name = "Câu hỏi thường gặp học phí"
        verbose_name_plural = "Danh sách FAQ học phí"
        ordering = ["order", "id"]

    def __str__(self):
        return self.question


class ChinhSachHocBong(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tên chính sách / Học bổng")
    icon = models.CharField(
        max_length=50, default="military_tech", verbose_name="Icon Material Symbols"
    )
    badge = models.CharField(
        max_length=100, blank=True, verbose_name="Huy hiệu / Điểm nổi bật"
    )
    summary = models.TextField(verbose_name="Tóm tắt")
    details = models.TextField(blank=True, verbose_name="Nội dung chi tiết")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        db_table = 'admissions_scholarship'
        verbose_name = "Chính sách học bổng / Miễn giảm"
        verbose_name_plural = "Danh sách Chính sách học bổng"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class TaiLieuTuyenSinh(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Đang chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('cho_duyet', 'Đang chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('tu_choi', 'Từ chối'),
    ]

    title = models.CharField(max_length=255, verbose_name="Tên tài liệu")
    file = models.FileField(upload_to="file_upload/", verbose_name="Tệp đính kèm")
    file_size = models.CharField(
        max_length=50, blank=True, verbose_name="Kích thước tệp"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái phê duyệt"
    )
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
        verbose_name="Người tải lên"
    )
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_documents",
        verbose_name="HĐTS phê duyệt"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Thời gian phê duyệt"
    )
    reject_reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Lý do từ chối"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Thời gian tải lên"
    )
    is_processed = models.BooleanField(default=False, verbose_name="Đã nạp vào AI")

    # Thuộc tính alias tiếng Việt theo thiết kế HĐTS
    @property
    def nguoi_upload(self):
        return self.uploaded_by

    @property
    def nguoi_duyet(self):
        return self.approved_by

    @property
    def ngay_duyet(self):
        return self.approved_at

    @property
    def trang_thai(self):
        return self.status

    @property
    def ly_do_tu_choi(self):
        return self.reject_reason

    class Meta:
        db_table = 'admissions_uploaded_file'
        verbose_name = "Tài liệu Tuyển sinh"
        verbose_name_plural = "Nguồn tài liệu Tuyển sinh (Cán bộ upload)"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"


# ========================================================
# 8. CÂU LẠC BỘ, ĐỘI, NHÓM SINH VIÊN (CLB)
# ========================================================

class CauLacBo(models.Model):
    FACULTY_CHOICES = [
        ('tcnh', 'Khoa Tài chính - Ngân hàng'),
        ('dlkdqt', 'Khoa Du lịch và kinh doanh quốc tế'),
        ('tmdt_mkt_cns', 'Khoa Thương mại điện tử - Marketing và Công nghệ số'),
        ('kt', 'Khoa Kinh tế'),
        ('qtkd', 'Khoa Quản trị kinh doanh'),
        ('ketoan', 'Khoa Kế toán'),
        ('llct', 'Khoa Lý luận chính trị'),
        ('luat', 'Khoa Luật'),
        ('vdtqt', 'Viện Đào tạo Quốc tế'),
    ]

    slug = models.SlugField(max_length=100, unique=True, verbose_name="Mã định danh (ID/Slug)")
    name = models.CharField(max_length=200, verbose_name="Tên Câu lạc bộ")
    aliases = models.JSONField(default=list, blank=True, verbose_name="Tên viết tắt / Bí danh")
    level = models.CharField(max_length=100, default="Trường (trực thuộc Hội SV)", verbose_name="Cấp trực thuộc")
    faculty_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã Khoa (nếu thuộc Khoa)")
    category = models.CharField(max_length=100, default="Kỹ năng và khởi nghiệp", verbose_name="Lĩnh vực hoạt động")
    founded = models.CharField(max_length=50, blank=True, verbose_name="Ngày thành lập")
    slogan = models.CharField(max_length=255, blank=True, verbose_name="Khẩu hiệu / Slogan")
    description = models.TextField(verbose_name="Mô tả chi tiết")
    intro = models.TextField(blank=True, verbose_name="Giới thiệu ngắn")
    mission = models.TextField(blank=True, verbose_name="Sứ mệnh")
    vision = models.TextField(blank=True, verbose_name="Tầm nhìn")

    departments = models.JSONField(default=list, blank=True, verbose_name="Các ban chuyên môn")
    contact = models.JSONField(default=dict, blank=True, verbose_name="Thông tin liên hệ (Facebook, Email...)")
    leaders = models.CharField(max_length=255, blank=True, verbose_name="Ban chủ nhiệm nhiệm kỳ")
    advisors = models.CharField(max_length=255, blank=True, verbose_name="Cố vấn chuyên môn")
    achievements = models.JSONField(default=list, blank=True, verbose_name="Thành tích và bằng khen")
    recruitment = models.CharField(max_length=200, blank=True, default="Mở đơn định kỳ tháng 8 - tháng 10", verbose_name="Thời gian tuyển quân")
    recruitment_steps = models.JSONField(default=list, blank=True, verbose_name="Các vòng ứng tuyển")
    benefits = models.JSONField(default=list, blank=True, verbose_name="Quyền lợi thành viên")
    followers = models.CharField(max_length=50, default="10K+", verbose_name="Lượng người theo dõi")

    logo = models.CharField(max_length=255, blank=True, verbose_name="Đường dẫn logo")
    cover = models.CharField(max_length=255, blank=True, verbose_name="Đường dẫn ảnh bìa cover")
    gallery = models.JSONField(default=list, blank=True, verbose_name="Thư viện ảnh")
    highlights = models.JSONField(default=list, blank=True, verbose_name="Điểm nổi bật")
    recent_activities = models.JSONField(default=list, blank=True, verbose_name="Hoạt động gần đây")

    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")

    class Meta:
        db_table = 'admissions_club'
        verbose_name = "Câu lạc bộ / Đội / Nhóm"
        verbose_name_plural = "8. Quản lý Câu lạc bộ – Đội – Nhóm (CLB)"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.level})"

    def to_dict(self):
        """Serialize thành dict chuẩn cho template và API"""
        fid = self.faculty_id
        faculty_name_map = dict(self.FACULTY_CHOICES)
        fac_name = faculty_name_map.get(fid, 'Cấp trường (Đoàn – Hội)' if not fid else fid)

        logo_url = None
        if self.logo:
            logo_clean = self.logo.replace('\\', '/').split('/')[-1]
            logo_url = f"/static/img/clb/{logo_clean}"

        cover_url = None
        if self.cover:
            cover_clean = self.cover.replace('\\', '/').split('/')[-1]
            cover_url = f"/static/img/clb/{cover_clean}"

        formatted_gallery = []
        for g in (self.gallery or []):
            if isinstance(g, dict):
                url = g.get('url', '')
                if url and not url.startswith('/'):
                    url_clean = url.replace('\\', '/').split('/')[-1]
                    url = f"/static/img/clb/{url_clean}"
                formatted_gallery.append({'url': url, 'caption': g.get('caption', '')})

        return {
            "id": self.slug,
            "name": self.name,
            "aliases": self.aliases or [],
            "level": self.level,
            "faculty_id": self.faculty_id,
            "faculty_name": fac_name,
            "category": self.category,
            "founded": self.founded,
            "slogan": self.slogan,
            "description": self.description,
            "intro": self.intro,
            "mission": self.mission,
            "vision": self.vision,
            "departments": self.departments or [],
            "contact": self.contact or {},
            "leaders": self.leaders,
            "advisors": self.advisors,
            "achievements": self.achievements or [],
            "recruitment": self.recruitment,
            "recruitment_steps": self.recruitment_steps or [],
            "benefits": self.benefits or [],
            "followers": self.followers,
            "logo": self.logo,
            "cover": self.cover,
            "logo_url": logo_url,
            "cover_url": cover_url,
            "gallery": formatted_gallery,
            "highlights": self.highlights or [],
            "recent_activities": self.recent_activities or []
        }


# ========================================================
# 9. ĐĂNG KÝ THÀNH VIÊN CLB
# ========================================================

class DangKyCLB(models.Model):
    TRANG_THAI_CHOICES = [
        ('cho_duyet', 'Chờ duyệt hồ sơ'),
        ('moi_phong_van', 'Mời phỏng vấn'),
        ('trung_tuyen', 'Trúng tuyển'),
        ('khong_dat', 'Không đạt'),
    ]

    clb = models.ForeignKey(CauLacBo, on_delete=models.CASCADE, related_name='don_dang_ky', verbose_name="Câu lạc bộ ứng tuyển")
    ho_ten = models.CharField(max_length=100, verbose_name="Họ và tên ứng viên")
    ma_sinh_vien = models.CharField(max_length=30, blank=True, verbose_name="Mã sinh viên (nếu có)")
    khoa_lop = models.CharField(max_length=150, blank=True, verbose_name="Khóa / Lớp / Trường THPT")
    so_dien_thoai = models.CharField(max_length=20, verbose_name="Số điện thoại")
    email = models.EmailField(verbose_name="Email liên hệ")
    facebook_link = models.URLField(blank=True, verbose_name="Link trang Facebook cá nhân")
    ban_ung_tuyen = models.CharField(max_length=100, blank=True, verbose_name="Ban chuyên môn nguyện vọng")
    kinh_nghiem = models.TextField(blank=True, verbose_name="Kinh nghiệm / Năng khiếu")
    ly_do_ung_tuyen = models.TextField(verbose_name="Lý do mong muốn tham gia CLB")
    trang_thai = models.CharField(max_length=30, choices=TRANG_THAI_CHOICES, default='cho_duyet', verbose_name="Trạng thái hồ sơ")
    ghi_chu_noi_bo = models.TextField(blank=True, verbose_name="Ghi chú đánh giá / Phỏng vấn")
    ngay_nop = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian nộp đơn")

    class Meta:
        db_table = 'admissions_club_registration'
        verbose_name = "Đơn đăng ký tham gia CLB"
        verbose_name_plural = "9. Đơn đăng ký thành viên CLB"
        ordering = ['-ngay_nop']

    def __str__(self):
        return f"{self.ho_ten} - Ứng tuyển {self.clb.name} [{self.get_trang_thai_display()}]"


# ========================================================
# 10. HỒ SƠ TƯ VẤN HƯỚNG NGHIỆP HOLLAND (RIASEC)
# ========================================================

class HoSoHuongNghiep(models.Model):
    GIOI_TINH_CHOICES = [
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ'),
        ('Khác', 'Khác'),
    ]

    ho_ten = models.CharField(max_length=100, verbose_name="Họ và tên học sinh")
    gioi_tinh = models.CharField(max_length=10, choices=GIOI_TINH_CHOICES, default='Nam', verbose_name="Giới tính")
    ngay_sinh = models.CharField(max_length=20, blank=True, verbose_name="Ngày sinh (DD/MM/YYYY)")
    so_dien_thoai = models.CharField(max_length=20, verbose_name="Số điện thoại")
    email = models.EmailField(verbose_name="Email liên hệ")
    truong_thpt = models.CharField(max_length=200, blank=True, verbose_name="Trường THPT đang học")
    tinh_thanh = models.CharField(max_length=100, blank=True, verbose_name="Tỉnh / Thành phố")
    dia_chi = models.CharField(max_length=255, blank=True, verbose_name="Địa chỉ cụ thể")

    so_thich = models.TextField(blank=True, verbose_name="Sở thích cá nhân")
    so_truong = models.TextField(blank=True, verbose_name="Sở trường / Thế mạnh")
    muc_tieu_nghe_nghiep = models.TextField(blank=True, verbose_name="Mục tiêu nghề nghiệp tương lai")

    # Điểm RIASEC Holland
    diem_r = models.PositiveSmallIntegerField(default=0, verbose_name="Điểm R (Realistic - Kỹ thuật)")
    diem_i = models.PositiveSmallIntegerField(default=0, verbose_name="Điểm I (Investigative - Nghiên cứu)")
    diem_a = models.PositiveSmallIntegerField(default=0, verbose_name="Điểm A (Artistic - Nghệ thuật)")
    diem_s = models.PositiveSmallIntegerField(default=0, verbose_name="Điểm S (Social - Xã hội)")
    diem_e = models.PositiveSmallIntegerField(default=0, verbose_name="Điểm E (Enterprising - Quản lý/Kinh doanh)")
    diem_c = models.PositiveSmallIntegerField(default=0, verbose_name="Điểm C (Conventional - Nghiệp vụ/Chi tiết)")
    ma_holland = models.CharField(max_length=20, blank=True, verbose_name="Mã Holland (Top 3)")
    nganh_de_xuat = models.TextField(blank=True, verbose_name="Danh sách ngành học DUE đề xuất")

    da_lien_he = models.BooleanField(default=False, verbose_name="Đã liên hệ tư vấn")
    ghi_chu_tu_van = models.TextField(blank=True, verbose_name="Ghi chú cán bộ tuyển sinh")
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian thực hiện")

    class Meta:
        db_table = 'admissions_career_profile'
        verbose_name = "Hồ sơ trắc nghiệm hướng nghiệp"
        verbose_name_plural = "10. Hồ sơ Trắc nghiệm Hướng nghiệp Holland"
        ordering = ['-ngay_tao']

    def __str__(self):
        return f"{self.ho_ten} ({self.so_dien_thoai}) - Mã: {self.ma_holland or 'Chưa xác định'}"


# ========================================================
# 11. HƯỚNG DẪN NHẬP HỌC VÀ LỊCH TRÌNH TÂN SINH VIÊN
# ========================================================

class HuongDanNhapHoc(models.Model):
    ma_huong_dan = models.CharField(max_length=50, unique=True, verbose_name="Mã hướng dẫn (ID)")
    chu_de = models.CharField(max_length=150, verbose_name="Chủ đề / Chuyên mục")
    cau_hoi = models.TextField(verbose_name="Tiêu đề / Câu hỏi tình huống")
    noi_dung = models.TextField(verbose_name="Nội dung giải đáp chi tiết")
    tu_khoa = models.TextField(blank=True, verbose_name="Từ khóa tra cứu")
    link_tai_lieu = models.CharField(max_length=300, blank=True, verbose_name="Link tài liệu / Website / Hotline")
    thu_tu = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    kich_hoat = models.BooleanField(default=True, verbose_name="Kích hoạt")

    class Meta:
        db_table = 'admissions_admission_guide'
        verbose_name = "Hướng dẫn nhập học tân SV"
        verbose_name_plural = "11. Cẩm nang Hướng dẫn Nhập học Khóa mới"
        ordering = ['thu_tu', 'id']

    def __str__(self):
        return f"[{self.chu_de}] {self.cau_hoi[:60]}"


class LichTrinhTanSinhVien(models.Model):
    LOAI_SU_KIEN_CHOICES = [
        ('ke_khai', 'Kê khai trực tuyến'),
        ('dong_hoc_phi', 'Nộp học phí tạm thu'),
        ('nop_ho_so', 'Nộp hồ sơ trực tiếp'),
        ('tuan_sinh_hoat', 'Tuần sinh hoạt công dân'),
        ('kham_suc_khoe', 'Khám sức khỏe'),
        ('khai_giang', 'Lễ Khai giảng'),
        ('khac', 'Hoạt động khác'),
    ]

    tieu_de = models.CharField(max_length=200, verbose_name="Tên hoạt động / Mốc sự kiện")
    thoi_gian = models.CharField(max_length=150, verbose_name="Thời gian diễn ra")
    dia_diem = models.CharField(max_length=200, default="Trường ĐH Kinh tế - ĐH Đà Nẵng", verbose_name="Địa điểm")
    doi_tuong = models.CharField(max_length=150, default="Tân sinh viên Khóa 52K", verbose_name="Đối tượng tham gia")
    noi_dung = models.TextField(verbose_name="Nội dung chi tiết và lưu ý")
    loai_su_kien = models.CharField(max_length=30, choices=LOAI_SU_KIEN_CHOICES, default='khac', verbose_name="Phân loại sự kiện")
    thu_tu = models.PositiveIntegerField(default=0, verbose_name="Thứ tự thời gian")
    kich_hoat = models.BooleanField(default=True, verbose_name="Kích hoạt")

    class Meta:
        db_table = 'admissions_freshman_schedule'
        verbose_name = "Mốc lịch trình tân sinh viên"
        verbose_name_plural = "12. Lịch trình sự kiện Tân sinh viên"
        ordering = ['thu_tu', 'id']

    def __str__(self):
        return f"{self.tieu_de} ({self.thoi_gian})"



class DocumentChunk(models.Model):
    document = models.ForeignKey(
        TaiLieuTuyenSinh,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    source = models.CharField(max_length=255, verbose_name="Nguồn")
    chunk_index = models.PositiveIntegerField(default=0)
    content = models.TextField()
    embedding = models.JSONField()  # list 1024 số float


    class Meta:
        db_table = 'admissions_document_chunk'

    def __str__(self):
        return f"{self.source} #{self.chunk_index}"


# ========================================================
# 13. CÂU HỎI CHATBOT CHUYỂN CHO CÁN BỘ TUYỂN SINH
# ========================================================

class CauHoiChoTraLoi(models.Model):
    TRANG_THAI_CHOICES = [
        ('cho', 'Đang chờ cán bộ trả lời'),
        ('da_tra_loi', 'Đã trả lời'),
    ]

    client_id = models.CharField(max_length=64, db_index=True, verbose_name="Mã phiên người hỏi")
    cau_hoi = models.TextField(verbose_name="Câu hỏi")
    ngu_canh = models.TextField(blank=True, verbose_name="Hội thoại trước đó")
    tra_loi = models.TextField(blank=True, verbose_name="Câu trả lời của cán bộ")
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='cho', db_index=True, verbose_name="Trạng thái")
    nguoi_hoi = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='cau_hoi_da_gui', verbose_name="Người gửi câu hỏi")
    can_bo = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cán bộ trả lời")
    da_them_kien_thuc = models.BooleanField(default=False, verbose_name="Đã thêm vào kho kiến thức")
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian hỏi")
    ngay_tra_loi = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian trả lời")

    class Meta:
        db_table = 'admissions_pending_question'
        verbose_name = "Câu hỏi chờ cán bộ trả lời"
        verbose_name_plural = "13. Câu hỏi Chatbot chờ cán bộ trả lời"
        ordering = ['-ngay_tao']

    def __str__(self):
        return f"[{self.get_trang_thai_display()}] {self.cau_hoi[:60]}"


# ========================================================
# 14. LỊCH SỬ CHAT VÀ PHIÊN TRÒ CHUYỆN CỦA NGƯỜI DÙNG
# ========================================================

class ChatSession(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_sessions",
        verbose_name="Người dùng"
    )
    session_id = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Mã phiên chat")
    title = models.CharField(max_length=255, default="Cuộc trò chuyện mới", verbose_name="Tiêu đề phiên chat")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật gần nhất")

    class Meta:
        db_table = 'admissions_chat_session'
        verbose_name = "Phiên hội thoại Chatbot"
        verbose_name_plural = "14. Phiên hội thoại Chatbot"
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.session_id})"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'Người dùng'),
        ('assistant', 'Trợ lý AI DUE'),
        ('officer', 'Cán bộ tư vấn'),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Phiên chat"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Vai trò")
    content = models.TextField(verbose_name="Nội dung tin nhắn")
    sources = models.JSONField(default=list, blank=True, verbose_name="Nguồn trích dẫn")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian gửi")

    class Meta:
        db_table = 'admissions_chat_message'
        verbose_name = "Tin nhắn Chatbot"
        verbose_name_plural = "Tin nhắn Chatbot"
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:50]}"


class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile', verbose_name="Tài khoản")
    full_name = models.CharField(max_length=150, blank=True, verbose_name="Họ và tên")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Số điện thoại")
    cccd = models.CharField(max_length=50, blank=True, verbose_name="Số CCCD")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng ký")

    class Meta:
        db_table = 'admissions_user_profile'
        verbose_name = "Hồ sơ người dùng / Thí sinh"
        verbose_name_plural = "Hồ sơ người dùng / Thí sinh"

    def __str__(self):
        return f"{self.user.username} - {self.full_name or self.phone or self.user.email}"


# ========================================================
# 15. THÔNG BÁO HỆ THỐNG (IN-APP NOTIFICATIONS)
# ========================================================

class ThongBao(models.Model):
    LOAI_CHOICES = [
        ('upload_moi', 'Tài liệu mới cần duyệt'),
        ('da_duyet', 'Tài liệu đã được duyệt'),
        ('tu_choi', 'Tài liệu bị từ chối'),
        ('he_thong', 'Thông báo hệ thống'),
    ]

    nguoi_nhan = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name="thong_bao_nhan",
        verbose_name="Người nhận"
    )
    nguoi_gui = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="thong_bao_gui",
        verbose_name="Người gửi"
    )
    tieu_de = models.CharField(max_length=255, verbose_name="Tiêu đề thông báo")
    noi_dung = models.TextField(verbose_name="Nội dung thông báo")
    loai = models.CharField(
        max_length=50,
        choices=LOAI_CHOICES,
        default='he_thong',
        verbose_name="Phân loại thông báo"
    )
    tai_lieu = models.ForeignKey(
        TaiLieuTuyenSinh,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="thong_bao_lien_quan",
        verbose_name="Tài liệu liên quan"
    )
    duong_dan = models.CharField(max_length=255, blank=True, default='', verbose_name="Đường dẫn xử lý")
    da_doc = models.BooleanField(default=False, db_index=True, verbose_name="Đã đọc")
    ngay_tao = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Thời gian tạo")

    class Meta:
        db_table = 'admissions_notification'
        verbose_name = "Thông báo hệ thống"
        verbose_name_plural = "15. Quản lý Thông báo hệ thống"
        ordering = ['-ngay_tao']

    def __str__(self):
        return f"[{self.get_loai_display()}] {self.tieu_de} -> {self.nguoi_nhan.username}"



