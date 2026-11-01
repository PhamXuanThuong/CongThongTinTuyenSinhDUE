from django.db import models

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


# =====================================================================
# MODELS FOR HƯỚNG DẪN NHẬP HỌC & LỊCH TRÌNH TÂN SINH VIÊN
# =====================================================================

class DotNhapHoc(models.Model):
    title = models.CharField(max_length=200, default="Khóa 52K - Tuyển sinh năm 2026", verbose_name="Tên đợt / Khóa tuyển sinh")
    academic_year = models.CharField(max_length=50, default="2026 - 2027", verbose_name="Năm học")
    online_portal_url = models.URLField(default="https://nhaphoc.due.udn.vn", verbose_name="Cổng nhập học online")
    online_deadline = models.CharField(max_length=150, default="Trước 17h00 ngày 25/08/2026", verbose_name="Thời hạn xác nhận online")
    onsite_time = models.CharField(max_length=150, default="Từ ngày 03/09/2026 đến ngày 05/09/2026 (Sáng: 07h30 - 11h30, Chiều: 13h30 - 17h00)", verbose_name="Thời gian nộp hồ sơ trực tiếp")
    onsite_location = models.CharField(max_length=255, default="Hội trường E, Trường Đại học Kinh tế - ĐHĐN (71 Ngũ Hành Sơn, TP. Đà Nẵng)", verbose_name="Địa điểm nộp trực tiếp")
    bank_account_name = models.CharField(max_length=200, default="Trường Đại học Kinh tế - Đại học Đà Nẵng", verbose_name="Tên tài khoản thụ hưởng")
    bank_account_number = models.CharField(max_length=50, default="113000000000", verbose_name="Số tài khoản ngân hàng")
    bank_name = models.CharField(max_length=150, default="VietinBank - Chi nhánh Nam Đà Nẵng", verbose_name="Ngân hàng")
    transfer_syntax = models.CharField(max_length=255, default="[Mã hồ sơ/CCCD] - [Họ và tên] - Nhap hoc K52", verbose_name="Cú pháp chuyển khoản")
    hotline = models.CharField(max_length=100, default="(0236) 3950 110 - (0236) 3836 169", verbose_name="Hotline hỗ trợ")
    email_support = models.CharField(max_length=100, default="tuyensinh@due.edu.vn", verbose_name="Email hỗ trợ")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")

    class Meta:
        verbose_name = "Thông tin Đợt nhập học"
        verbose_name_plural = "Cấu hình Đợt nhập học"

    def __str__(self):
        return f"{self.title} ({self.academic_year})"


class KhoanThuNhapHoc(models.Model):
    CATEGORY_CHOICES = [
        ('bat_buoc', 'I. Khoản thu bắt buộc'),
        ('theo_nhu_cau', 'II. Khoản thu theo nhu cầu / Tùy chọn'),
    ]

    dot_nhap_hoc = models.ForeignKey(DotNhapHoc, on_delete=models.CASCADE, related_name="fees", null=True, blank=True, verbose_name="Thuộc đợt nhập học")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='bat_buoc', verbose_name="Phân loại")
    item_order = models.PositiveIntegerField(default=1, verbose_name="STT hiển thị")
    name = models.CharField(max_length=255, verbose_name="Tên khoản thu")
    amount = models.CharField(max_length=150, verbose_name="Mức thu", help_text="Ví dụ: 1.600.000 đồng hoặc Xem chi tiết tại đây")
    detail_link = models.CharField(max_length=255, blank=True, verbose_name="Link chi tiết (nếu có)", help_text="Ví dụ: /hoc-phi/")
    note = models.CharField(max_length=255, blank=True, verbose_name="Ghi chú thêm")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        verbose_name = "Khoản thu nhập học"
        verbose_name_plural = "Danh mục Khoản thu nhập học"
        ordering = ['category', 'order', 'item_order']

    def __str__(self):
        return f"{self.name} - {self.amount}"


class HoSoNhapHoc(models.Model):
    CATEGORY_CHOICES = [
        ('ca_nhan', 'I. Hồ sơ cá nhân'),
        ('xet_tuyen', 'II. Minh chứng xét tuyển'),
    ]

    dot_nhap_hoc = models.ForeignKey(DotNhapHoc, on_delete=models.CASCADE, related_name="documents", null=True, blank=True, verbose_name="Thuộc đợt nhập học")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='ca_nhan', verbose_name="Nhóm hồ sơ")
    item_order = models.PositiveIntegerField(default=1, verbose_name="STT")
    title = models.CharField(max_length=255, verbose_name="Tên loại giấy tờ / Hồ sơ")
    requirement = models.CharField(max_length=200, verbose_name="Quy cách nộp", help_text="Ví dụ: Bản chính, Bản sao công chứng (trong vòng 6 tháng)...")
    download_url = models.URLField(blank=True, verbose_name="Link tải biểu mẫu (nếu có)")
    note = models.CharField(max_length=255, blank=True, verbose_name="Ghi chú hướng dẫn")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        verbose_name = "Giấy tờ hồ sơ nhập học"
        verbose_name_plural = "Danh mục Hồ sơ nhập học"
        ordering = ['order', 'item_order']

    def __str__(self):
        return f"{self.item_order}. {self.title}"


class BieuMauNhapHoc(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tên biểu mẫu")
    file = models.FileField(upload_to="bieu_mau/", blank=True, null=True, verbose_name="File đính kèm (.pdf, .docx)")
    external_link = models.URLField(blank=True, verbose_name="Link ngoài (nếu không upload file)")
    file_type = models.CharField(max_length=20, default="PDF", verbose_name="Loại tệp")
    file_size = models.CharField(max_length=50, blank=True, default="150 KB", verbose_name="Dung lượng hiển thị")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")

    class Meta:
        verbose_name = "Biểu mẫu đính kèm"
        verbose_name_plural = "Danh sách Biểu mẫu nhập học"
        ordering = ['order', 'id']

    def __str__(self):
        return self.title

    @property
    def download_url(self):
        if self.file:
            return self.file.url
        return self.external_link or "#"


class MocLichTrinhTsv(models.Model):
    milestone_number = models.PositiveIntegerField(default=1, verbose_name="Mốc số")
    title = models.CharField(max_length=255, verbose_name="Tiêu đề mốc lịch trình")
    time_range = models.CharField(max_length=150, verbose_name="Thời gian thực hiện", help_text="Ví dụ: 20/08 - 25/08/2026")
    location = models.CharField(max_length=255, blank=True, verbose_name="Địa điểm")
    badge_text = models.CharField(max_length=50, default="Quan trọng", verbose_name="Nhãn trạng thái (Badge)")
    badge_color = models.CharField(max_length=100, default="bg-amber-100 text-amber-800 border-amber-200", verbose_name="Màu nhãn")
    summary = models.TextField(verbose_name="Tóm tắt công việc cần làm")
    description_html = models.TextField(blank=True, verbose_name="Nội dung chi tiết (HTML hoặc các gạch đầu dòng)")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")

    class Meta:
        verbose_name = "Mốc lịch trình Tân sinh viên"
        verbose_name_plural = "Lịch trình Tân sinh viên (5 Mốc)"
        ordering = ['order', 'milestone_number']

    def __str__(self):
        return f"Mốc {self.milestone_number}: {self.title}"
