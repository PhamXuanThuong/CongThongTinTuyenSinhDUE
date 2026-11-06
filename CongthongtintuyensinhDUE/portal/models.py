from django.db import models
from typing import List, Dict, Any, Optional
import os


class Faculty(models.Model):
    """
    Model lưu trữ Khoa / Viện đào tạo (dữ liệu từ khoa.json).
    db_table: portal_faculty
    """
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã định danh (ID/Slug)", help_text="Ví dụ: tcnh, dlkdqt...")
    name = models.CharField(max_length=200, verbose_name="Tên Khoa / Viện")
    faculty_type = models.CharField(max_length=50, default="faculty", verbose_name="Loại (faculty/institute)")
    url = models.URLField(blank=True, null=True, default="", verbose_name="Website chính thức")
    slogan = models.CharField(max_length=255, blank=True, null=True, default="", verbose_name="Khẩu hiệu / Slogan")
    intro = models.TextField(blank=True, null=True, default="", verbose_name="Giới thiệu")
    mission = models.TextField(blank=True, null=True, default="", verbose_name="Sứ mệnh")
    vision = models.TextField(blank=True, null=True, default="", verbose_name="Tầm nhìn")
    history = models.TextField(blank=True, null=True, verbose_name="Lịch sử hình thành")
    staff_summary = models.CharField(max_length=255, blank=True, null=True, default="", verbose_name="Tóm tắt đội ngũ")
    dean_message = models.TextField(blank=True, null=True, default="", verbose_name="Thông điệp Trưởng khoa")

    # Dữ liệu có cấu trúc JSON
    formed_from = models.JSONField(default=list, blank=True, verbose_name="Hình thành từ")
    achievements = models.JSONField(default=list, blank=True, verbose_name="Thành tích nổi bật")
    career_paths = models.JSONField(default=list, blank=True, verbose_name="Định hướng nghề nghiệp")
    notable_activities = models.JSONField(default=list, blank=True, verbose_name="Hoạt động tiêu biểu")
    leadership = models.JSONField(default=dict, blank=True, verbose_name="Ban lãnh đạo khoa")
    departments = models.JSONField(default=list, blank=True, verbose_name="Bộ môn trực thuộc")
    postgraduate = models.JSONField(default=list, blank=True, verbose_name="Chương trình sau đại học")
    special_programs = models.JSONField(default=list, blank=True, verbose_name="Chương trình đặc thù")
    contact = models.JSONField(default=dict, blank=True, verbose_name="Thông tin liên hệ")
    links = models.JSONField(default=dict, blank=True, verbose_name="Liên kết mạng xã hội")
    major_ids = models.JSONField(default=list, blank=True, verbose_name="Mã các ngành đào tạo")
    majors_2026 = models.JSONField(default=list, blank=True, verbose_name="Thông tin ngành tuyển sinh 2026")
    lien_chi_doan = models.JSONField(default=list, blank=True, verbose_name="Dữ liệu liên chi đoàn gốc")
    clubs = models.JSONField(default=list, blank=True, verbose_name="CLB")
    why_choose = models.JSONField(default=list, blank=True, verbose_name="Lý do chọn khoa")
    staff_stats = models.JSONField(default=dict, blank=True, verbose_name="Thống kê giảng viên")
    partners = models.JSONField(default=list, blank=True, verbose_name="Đối tác doanh nghiệp")
    student_activities = models.JSONField(default=list, blank=True, verbose_name="Hoạt động sinh viên")
    clubs_details = models.JSONField(default=list, blank=True, verbose_name="CLB trực thuộc khoa")
    gallery = models.JSONField(default=list, blank=True, verbose_name="Thư viện ảnh")
    aliases = models.JSONField(default=list, blank=True, verbose_name="Tên viết tắt / Tên gọi khác")
    
    # Dữ liệu Liên Chi Đoàn (LCD)
    lcd = models.JSONField(default=dict, blank=True, verbose_name="Thông tin Liên Chi Đoàn")

    # Thuộc tính giao diện
    icon = models.CharField(max_length=50, default="school", verbose_name="Icon Material")
    color = models.CharField(max_length=50, default="bg-blue-600", verbose_name="Màu badge/chủ đạo")
    border_color = models.CharField(max_length=50, blank=True, default="", verbose_name="Màu border")
    text_color = models.CharField(max_length=50, blank=True, default="", verbose_name="Màu text")
    light_bg = models.CharField(max_length=50, blank=True, default="", verbose_name="Màu nền nhạt")
    gradient = models.CharField(max_length=100, default="from-blue-600 to-indigo-700", verbose_name="Gradient Tailwind")
    badge_color = models.CharField(max_length=50, blank=True, default="", verbose_name="Màu badge")
    category_tag = models.CharField(max_length=100, blank=True, default="", verbose_name="Tag phân loại")

    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")

    class Meta:
        db_table = 'portal_faculty'
        verbose_name = "Khoa / Viện Đào Tạo"
        verbose_name_plural = "Danh sách Khoa / Viện"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary hoàn chỉnh chuẩn khớp với template frontend"""
        fid = self.code
        lcd_data = dict(self.lcd) if self.lcd else {}
        
        # Đảm bảo các url ảnh và chi tiết được format đúng
        lcd_data['detail_url'] = f'/lien-chi-doan/{fid}/'
        lcd_data['faculty_id'] = fid
        lcd_data['faculty_name'] = self.name
        lcd_data['color'] = self.color or 'bg-blue-600'
        lcd_data['gradient'] = self.gradient or 'from-blue-600 to-indigo-700'
        
        if 'images' in lcd_data and isinstance(lcd_data['images'], list):
            for img in lcd_data['images']:
                if isinstance(img, dict) and 'url' in img:
                    if not img['url'].startswith('/'):
                        img['url'] = f'/static/img/lcd/{os.path.basename(img["url"])}'

        formatted_gallery = []
        for g in (self.gallery or []):
            if isinstance(g, dict) and 'url' in g:
                url = g['url']
                if not url.startswith('/'):
                    url = f'/static/img/khoa/{os.path.basename(url)}'
                formatted_gallery.append({**g, 'url': url})
            else:
                formatted_gallery.append(g)

        return {
            'id': self.code,
            'code': self.code,
            'name': self.name,
            'type': self.faculty_type,
            'url': self.url,
            'slogan': self.slogan,
            'intro': self.intro,
            'mission': self.mission,
            'vision': self.vision,
            'history': self.history,
            'staff_summary': self.staff_summary,
            'dean_message': self.dean_message,
            'formed_from': self.formed_from or [],
            'achievements': self.achievements or [],
            'career_paths': self.career_paths or [],
            'notable_activities': self.notable_activities or [],
            'leadership': self.leadership or {},
            'departments': self.departments or [],
            'postgraduate': self.postgraduate or [],
            'special_programs': self.special_programs or [],
            'contact': self.contact or {},
            'links': self.links or {},
            'major_ids': self.major_ids or [],
            'majors_2026': self.majors_2026 or [],
            'lien_chi_doan': self.lien_chi_doan or [],
            'clubs': self.clubs or [],
            'why_choose': self.why_choose or [],
            'staff_stats': self.staff_stats or {},
            'partners': self.partners or [],
            'student_activities': self.student_activities or [],
            'clubs_details': self.clubs_details or [],
            'gallery': formatted_gallery,
            'aliases': self.aliases or [],
            'icon': self.icon or 'school',
            'color': self.color or 'bg-blue-600',
            'border_color': self.border_color,
            'text_color': self.text_color,
            'light_bg': self.light_bg,
            'gradient': self.gradient or 'from-blue-600 to-indigo-700',
            'badge_color': self.badge_color,
            'category_tag': self.category_tag,
            'logo_url': f'/static/img/khoa/{fid}_logo.png',
            'cover_url': f'/static/img/khoa/{fid}_cover.jpg',
            'detail_url': f'/khoa/{fid}/',
            'lcd_url': f'/lien-chi-doan/{fid}/',
            'lcd': lcd_data
        }


class Department(models.Model):
    """
    Model lưu trữ Phòng Ban Chức Năng / Trung Tâm (dữ liệu từ phongban.json).
    db_table: portal_department
    """
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã phòng ban (Slug)", help_text="Ví dụ: pb-ctsv, pb-dao-tao...")
    name = models.CharField(max_length=200, verbose_name="Tên phòng ban / Trung tâm")
    short_name = models.CharField(max_length=100, blank=True, default="", verbose_name="Tên rút gọn")
    tagline = models.CharField(max_length=255, blank=True, default="", verbose_name="Khẩu hiệu")
    desc = models.TextField(blank=True, default="", verbose_name="Mô tả chức năng")
    functions = models.JSONField(default=list, blank=True, verbose_name="Chức năng nhiệm vụ")
    duties = models.JSONField(default=list, blank=True, verbose_name="Nhiệm vụ cụ thể")
    location = models.CharField(max_length=255, blank=True, default="", verbose_name="Địa điểm phòng làm việc")
    phone = models.CharField(max_length=50, blank=True, default="", verbose_name="Số điện thoại")
    email = models.CharField(max_length=100, blank=True, default="", verbose_name="Email")
    fanpage = models.URLField(blank=True, default="", verbose_name="Link Fanpage")
    icon = models.CharField(max_length=50, default="domain", verbose_name="Icon Material")
    color = models.CharField(max_length=50, default="bg-blue-600", verbose_name="Màu badge/theme")
    badge = models.CharField(max_length=100, blank=True, default="", verbose_name="Nhãn hiển thị")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")

    class Meta:
        db_table = 'portal_department'
        verbose_name = "Phòng Ban Chức Năng"
        verbose_name_plural = "Danh sách Phòng Ban"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary hoàn chỉnh cho template/API"""
        return {
            'code': self.code,
            'name': self.name,
            'short_name': self.short_name or self.name,
            'tagline': self.tagline,
            'desc': self.desc,
            'functions': self.functions or [],
            'duties': self.duties or [],
            'location': self.location,
            'phone': self.phone,
            'email': self.email,
            'fanpage': self.fanpage,
            'icon': self.icon or 'domain',
            'color': self.color or 'bg-blue-600',
            'badge': self.badge
        }
