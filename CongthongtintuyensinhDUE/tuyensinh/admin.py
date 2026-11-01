from django.contrib import admin
from .models import (
    KhoaPhongBan, ChuyenNganh, BangHocPhi, CauHoiHocPhi, ChinhSachHocBong,
    DotNhapHoc, KhoanThuNhapHoc, HoSoNhapHoc, BieuMauNhapHoc, MocLichTrinhTsv
)

class ChuyenNganhInline(admin.TabularInline):
    model = ChuyenNganh
    extra = 1

@admin.register(KhoaPhongBan)
class KhoaPhongBanAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'code', 'phone', 'email', 'order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'code', 'description', 'email')
    ordering = ('category', 'order', 'name')
    inlines = [ChuyenNganhInline]

@admin.register(ChuyenNganh)
class ChuyenNganhAdmin(admin.ModelAdmin):
    list_display = ('name', 'khoa', 'note', 'order')
    list_filter = ('khoa',)
    search_fields = ('name', 'note', 'khoa__name')
    ordering = ('khoa', 'order')

@admin.register(BangHocPhi)
class BangHocPhiAdmin(admin.ModelAdmin):
    list_display = ('nhom', 'nam_hoc_1', 'nam_hoc_2', 'nam_hoc_3', 'nam_hoc_4', 'order', 'is_active')
    list_editable = ('nam_hoc_1', 'nam_hoc_2', 'nam_hoc_3', 'nam_hoc_4', 'order', 'is_active')

@admin.register(CauHoiHocPhi)
class CauHoiHocPhiAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('question', 'answer')

@admin.register(ChinhSachHocBong)
class ChinhSachHocBongAdmin(admin.ModelAdmin):
    list_display = ('title', 'badge', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'summary')


# -------------------------------------------------------------
# ADMIN FOR HƯỚNG DẪN NHẬP HỌC & LỊCH TRÌNH TÂN SINH VIÊN
# -------------------------------------------------------------

class KhoanThuNhapHocInline(admin.TabularInline):
    model = KhoanThuNhapHoc
    extra = 1
    fields = ('item_order', 'category', 'name', 'amount', 'detail_link', 'note', 'order')

class HoSoNhapHocInline(admin.TabularInline):
    model = HoSoNhapHoc
    extra = 1
    fields = ('item_order', 'title', 'requirement', 'note', 'order')

@admin.register(DotNhapHoc)
class DotNhapHocAdmin(admin.ModelAdmin):
    list_display = ('title', 'academic_year', 'online_deadline', 'onsite_time', 'is_active')
    list_filter = ('is_active', 'academic_year')
    search_fields = ('title', 'academic_year', 'onsite_location')
    inlines = [KhoanThuNhapHocInline, HoSoNhapHocInline]

@admin.register(KhoanThuNhapHoc)
class KhoanThuNhapHocAdmin(admin.ModelAdmin):
    list_display = ('item_order', 'name', 'category', 'amount', 'detail_link', 'order')
    list_filter = ('category',)
    list_editable = ('amount', 'detail_link', 'order')
    search_fields = ('name', 'note')
    ordering = ('category', 'order', 'item_order')

@admin.register(HoSoNhapHoc)
class HoSoNhapHocAdmin(admin.ModelAdmin):
    list_display = ('item_order', 'title', 'requirement', 'order')
    list_editable = ('requirement', 'order')
    search_fields = ('title', 'requirement', 'note')
    ordering = ('order', 'item_order')

@admin.register(BieuMauNhapHoc)
class BieuMauNhapHocAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'file_size', 'file', 'order', 'is_active')
    list_editable = ('file_type', 'file_size', 'order', 'is_active')
    search_fields = ('title',)
    ordering = ('order', 'id')

@admin.register(MocLichTrinhTsv)
class MocLichTrinhTsvAdmin(admin.ModelAdmin):
    list_display = ('milestone_number', 'title', 'time_range', 'location', 'badge_text', 'order', 'is_active')
    list_editable = ('time_range', 'location', 'badge_text', 'order', 'is_active')
    search_fields = ('title', 'time_range', 'location', 'summary')
    ordering = ('order', 'milestone_number')
