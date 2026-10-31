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
