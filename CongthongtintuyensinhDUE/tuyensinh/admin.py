from django.contrib import admin
from .models import KhoaPhongBan, ChuyenNganh, BangHocPhi, CauHoiHocPhi, ChinhSachHocBong

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
