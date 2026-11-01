from django.db import models
from django.utils.text import slugify

class TinTuc(models.Model):
    THE_LOAI_CHOICES = [
        ('tuyen_sinh', 'Tuyển sinh'),
        ('workshop', 'Workshop & Hướng nghiệp'),
        ('hoc_bong', 'Học bổng & Chính sách'),
        ('su_kien', 'Sự kiện & Hoạt động'),
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
        verbose_name = "Bản tin tuyển sinh & Sự kiện"
        verbose_name_plural = "1. Quản lý Tin tức & Sự kiện"
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
    mo_ta = models.TextField(verbose_name="Mô tả đặc điểm & ưu thế")
    ngon_ngu = models.CharField(max_length=100, default="Tiếng Việt & Tiếng Anh", verbose_name="Ngôn ngữ giảng dạy")
    thoi_gian_dao_tao = models.CharField(max_length=50, default="4 năm (8 học kỳ)", verbose_name="Thời gian đào tạo")
    bang_cap = models.CharField(max_length=150, default="Cử nhân chính quy", verbose_name="Bằng cấp tốt nghiệp")
    icon = models.CharField(max_length=50, default="school", verbose_name="Biểu tượng Material Symbol")
    thu_tu = models.PositiveIntegerField(default=1, verbose_name="Thứ tự hiển thị")

    class Meta:
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
    mo_ta = models.TextField(blank=True, verbose_name="Mô tả ngành & cơ hội việc làm")

    class Meta:
        verbose_name = "Ngành đào tạo & Chỉ tiêu"
        verbose_name_plural = "3. Danh mục Ngành & Chỉ tiêu tuyển sinh"
        ordering = ['ma_nganh']

    def __str__(self):
        return f"{self.ma_nganh} - {self.ten_nganh}"


class DiemChuan(models.Model):
    PHUONG_THUC_CHOICES = [
        ('THPT', 'Điểm thi tốt nghiệp THPT'),
        ('HOC_BA', 'Xét học bạ THPT kết hợp'),
        ('DGNL', 'Đánh giá năng lực ĐHQG-HCM'),
        ('XTT', 'Xét tuyển thẳng & Ưu tiên'),
    ]

    nganh = models.ForeignKey(NganhDaoTao, on_delete=models.CASCADE, related_name='diem_chuan_cac_nam', verbose_name="Ngành đào tạo")
    nam = models.PositiveIntegerField(verbose_name="Năm tuyển sinh (2025, 2024, 2023, 2022)")
    phuong_thuc = models.CharField(max_length=20, choices=PHUONG_THUC_CHOICES, default='THPT', verbose_name="Phương thức xét tuyển")
    diem_trung_tuyen = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Điểm chuẩn trúng tuyển")
    to_hop_xet_tuyen = models.CharField(max_length=100, blank=True, default="A00, A01, D01, D07", verbose_name="Tổ hợp áp dụng")
    tieu_chi_phu = models.CharField(max_length=255, blank=True, verbose_name="Tiêu chí phụ (nếu có)")
    ghi_chu = models.CharField(max_length=255, blank=True, verbose_name="Ghi chú")

    class Meta:
        verbose_name = "Điểm chuẩn theo năm"
        verbose_name_plural = "4. Điểm chuẩn trúng tuyển các năm"
        ordering = ['-nam', 'nganh__ma_nganh', 'phuong_thuc']
        unique_together = ('nganh', 'nam', 'phuong_thuc')

    def __str__(self):
        return f"{self.nganh.ten_nganh} ({self.nam}) - {self.diem_trung_tuyen}đ [{self.get_phuong_thuc_display()}]"


class PhuongThucXetTuyen(models.Model):
    ma_phuong_thuc = models.CharField(max_length=20, unique=True, verbose_name="Mã phương thức (PT1, PT2,...)")
    ten_phuong_thuc = models.CharField(max_length=200, verbose_name="Tên phương thức xét tuyển")
    doi_tuong_ap_dung = models.TextField(verbose_name="Đối tượng & Điều kiện áp dụng")
    chuong_trinh_ap_dung = models.CharField(max_length=200, default="Áp dụng các chương trình đào tạo", verbose_name="Chương trình áp dụng")
    nguyen_tac_xet = models.TextField(blank=True, verbose_name="Nguyên tắc xét tuyển & Cách tính điểm")
    mau_sac = models.CharField(max_length=30, default="blue", verbose_name="Tone màu đại diện (blue, emerald, orange, amber)")
    thu_tu = models.PositiveIntegerField(default=1, verbose_name="Thứ tự hiển thị")

    class Meta:
        verbose_name = "Phương thức xét tuyển"
        verbose_name_plural = "5. Phương thức xét tuyển 2026"
        ordering = ['thu_tu']

    def __str__(self):
        return f"{self.ma_phuong_thuc} - {self.ten_phuong_thuc}"


class CauHoiThuongGap(models.Model):
    PHAN_LOAI_CHOICES = [
        ('GioiThieuChung', 'Tổng quan & Giới thiệu'),
        ('LichSuPhatTrien', 'Lịch sử phát triển'),
        ('SuMangTamNhin', 'Sứ mạng & Tầm nhìn'),
        ('PhuongThucXetTuyen', 'Phương thức xét tuyển'),
        ('ChiTieuNganhHoc', 'Chỉ tiêu & Ngành học'),
        ('DiemChuan', 'Điểm chuẩn & Xét tuyển'),
        ('HocPhiHocBong', 'Học phí & Học bổng'),
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
        verbose_name = "Hỏi đáp & Tri thức Chatbot"
        verbose_name_plural = "6. Tri thức Chatbot & Hỏi đáp tự động"
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
        ('khoa', 'Khoa Đào Tạo'),
        ('phong_ban', 'Phòng Ban Chức Năng / Trung Tâm'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name="Mã định danh (slug)", help_text="Ví dụ: khoa-marketing, pb-ctsv")
    name = models.CharField(max_length=200, verbose_name="Tên Khoa / Phòng ban")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='khoa', verbose_name="Loại đơn vị")
    tagline = models.CharField(max_length=255, blank=True, verbose_name="Khẩu hiệu / Định hướng")
    color = models.CharField(max_length=50, default="bg-blue-600", verbose_name="Màu badge/icon (Tailwind)")
    icon = models.CharField(max_length=50, default="school", verbose_name="Icon Material Symbols")
    description = models.TextField(verbose_name="Mô tả / Giới thiệu")
    careers_or_functions = models.TextField(verbose_name="Cơ hội việc làm / Chức năng chính")
    location = models.CharField(max_length=255, default="Trường ĐH Kinh tế - ĐH Đà Nẵng", verbose_name="Địa điểm phòng làm việc")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Số điện thoại liên hệ")
    email = models.CharField(max_length=100, blank=True, verbose_name="Email liên hệ")
    fanpage_url = models.URLField(blank=True, default="https://www.facebook.com/FaceDue", verbose_name="Link Fanpage")
    messenger_url = models.URLField(blank=True, default="https://m.me/FaceDue", verbose_name="Link Messenger")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")

    class Meta:
        verbose_name = "Khoa / Phòng Ban"
        verbose_name_plural = "Danh sách Khoa & Phòng Ban"
        ordering = ['order', 'id']

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
            "email": self.email
        }


class ChuyenNganh(models.Model):
    khoa = models.ForeignKey(KhoaPhongBan, on_delete=models.CASCADE, related_name="majors", verbose_name="Thuộc Khoa")
    name = models.CharField(max_length=200, verbose_name="Tên Ngành / Chuyên ngành")
    note = models.CharField(max_length=150, blank=True, verbose_name="Mã ngành hoặc ghi chú")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        verbose_name = "Chuyên ngành đào tạo"
        verbose_name_plural = "Danh sách Chuyên ngành"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.name} ({self.khoa.name})"


class BangHocPhi(models.Model):
    nhom = models.CharField(max_length=200, verbose_name="Nhóm chương trình")
    slug = models.CharField(max_length=50, blank=True, verbose_name="Mã nhóm", help_text="Dùng cho công cụ tính: tieu-chuan, tai-nang, toan-phan-ta, ban-phan-ta")
    nam_hoc_1 = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Năm học 2026 - 2027 (Triệu đồng)")
    nam_hoc_2 = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Năm học 2027 - 2028 (Triệu đồng)")
    nam_hoc_3 = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Năm học 2028 - 2029 (Triệu đồng)")
    nam_hoc_4 = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Năm học 2029 - 2030 (Triệu đồng)")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")

    class Meta:
        verbose_name = "Mức học phí"
        verbose_name_plural = "Bảng học phí các năm"
        ordering = ['order', 'id']

    def __str__(self):
        return self.nhom


class CauHoiHocPhi(models.Model):
    question = models.CharField(max_length=255, verbose_name="Câu hỏi")
    answer = models.TextField(verbose_name="Câu trả lời")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")

    class Meta:
        verbose_name = "Câu hỏi thường gặp học phí"
        verbose_name_plural = "Danh sách FAQ học phí"
        ordering = ['order', 'id']

    def __str__(self):
        return self.question


class ChinhSachHocBong(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tên chính sách / Học bổng")
    icon = models.CharField(max_length=50, default="military_tech", verbose_name="Icon Material Symbols")
    badge = models.CharField(max_length=100, blank=True, verbose_name="Huy hiệu / Điểm nổi bật")
    summary = models.TextField(verbose_name="Tóm tắt")
    details = models.TextField(blank=True, verbose_name="Nội dung chi tiết")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        verbose_name = "Chính sách học bổng / Miễn giảm"
        verbose_name_plural = "Danh sách Chính sách học bổng"
        ordering = ['order', 'id']

    def __str__(self):
        return self.title
