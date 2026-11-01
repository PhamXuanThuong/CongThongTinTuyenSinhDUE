import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import (
    TinTuc,
    LoaiHinhDaoTao,
    NganhDaoTao,
    DiemChuan,
    PhuongThucXetTuyen,
    CauHoiThuongGap,
    TuVanTuyenSinh
)

# Tùy biến tiêu đề Django Admin
admin.site.site_header = "CỔNG THÔNG TIN TUYỂN SINH DUE - HỆ THỐNG QUẢN TRỊ"
admin.site.site_title = "Quản trị Tuyển sinh DUE"
admin.site.index_title = "Bảng điều khiển & Quản trị dữ liệu Tuyển sinh"


@admin.register(TinTuc)
class TinTucAdmin(admin.ModelAdmin):
    list_display = ('tieu_de', 'the_loai_badge', 'ngay_dang', 'luot_xem', 'noi_bat')
    list_filter = ('the_loai', 'noi_bat', 'ngay_dang')
    search_fields = ('tieu_de', 'tom_tat', 'noi_dung')
    prepopulated_fields = {'slug': ('tieu_de',)}
    list_editable = ('noi_bat',)
    date_hierarchy = 'ngay_dang'

    def the_loai_badge(self, obj):
        colors = {
            'tuyen_sinh': '#fd761a',
            'workshop': '#2563eb',
            'hoc_bong': '#16a34a',
            'su_kien': '#9333ea',
        }
        color = colors.get(obj.the_loai, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
            color, obj.get_the_loai_display()
        )
    the_loai_badge.short_description = "Thể loại"


class DiemChuanInline(admin.TabularInline):
    model = DiemChuan
    extra = 1
    fields = ('nam', 'phuong_thuc', 'diem_trung_tuyen', 'to_hop_xet_tuyen', 'ghi_chu')


@admin.register(NganhDaoTao)
class NganhDaoTaoAdmin(admin.ModelAdmin):
    list_display = ('ma_nganh', 'ten_nganh', 'loai_hinh_display', 'chi_tieu', 'to_hop_mon', 'so_luong_diem_chuan')
    search_fields = ('ma_nganh', 'ten_nganh', 'khoa', 'to_hop_mon')
    list_filter = ('loai_hinh', 'khoa')
    inlines = [DiemChuanInline]

    def loai_hinh_display(self, obj):
        if not obj.loai_hinh:
            return "-"
        return obj.loai_hinh.ten_loai_hinh
    loai_hinh_display.short_description = "Loại hình"

    def so_luong_diem_chuan(self, obj):
        count = obj.diem_chuan_cac_nam.count()
        return format_html('<b>{} bản ghi</b>', count)
    so_luong_diem_chuan.short_description = "Điểm chuẩn"


@admin.register(DiemChuan)
class DiemChuanAdmin(admin.ModelAdmin):
    list_display = ('nganh_ma', 'nganh_ten', 'nam', 'phuong_thuc_badge', 'diem_trung_tuyen', 'to_hop_xet_tuyen')
    list_filter = ('nam', 'phuong_thuc', 'nganh__loai_hinh')
    search_fields = ('nganh__ma_nganh', 'nganh__ten_nganh', 'to_hop_xet_tuyen')
    ordering = ('-nam', 'nganh__ma_nganh')

    def nganh_ma(self, obj):
        return obj.nganh.ma_nganh
    nganh_ma.short_description = "Mã ngành"

    def nganh_ten(self, obj):
        return obj.nganh.ten_nganh
    nganh_ten.short_description = "Tên ngành"

    def phuong_thuc_badge(self, obj):
        colors = {
            'THPT': '#ea580c',
            'HOC_BA': '#059669',
            'DGNL': '#d97706',
            'XTT': '#2563eb',
        }
        color = colors.get(obj.phuong_thuc, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 8px; font-weight: 600; font-size: 11px;">{}</span>',
            color, obj.get_phuong_thuc_display()
        )
    phuong_thuc_badge.short_description = "Phương thức"


@admin.register(LoaiHinhDaoTao)
class LoaiHinhDaoTaoAdmin(admin.ModelAdmin):
    list_display = ('ma_loai_hinh', 'ten_loai_hinh', 'ngon_ngu', 'thoi_gian_dao_tao', 'thu_tu')
    list_editable = ('thu_tu',)
    search_fields = ('ten_loai_hinh', 'mo_ta')


@admin.register(PhuongThucXetTuyen)
class PhuongThucXetTuyenAdmin(admin.ModelAdmin):
    list_display = ('ma_phuong_thuc', 'ten_phuong_thuc', 'chuong_trinh_ap_dung', 'mau_sac', 'thu_tu')
    list_editable = ('thu_tu',)
    search_fields = ('ma_phuong_thuc', 'ten_phuong_thuc', 'doi_tuong_ap_dung')


@admin.register(CauHoiThuongGap)
class CauHoiThuongGapAdmin(admin.ModelAdmin):
    list_display = ('ma_cau_hoi', 'chu_de', 'phan_loai', 'kich_hoat')
    list_filter = ('phan_loai', 'kich_hoat')
    search_fields = ('ma_cau_hoi', 'chu_de', 'cau_hoi_mau', 'cau_tra_loi', 'tu_khoa')
    list_editable = ('kich_hoat',)


def export_tu_van_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="danh_sach_tu_van_due.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Họ tên', 'Số điện thoại', 'Email', 'Ngành quan tâm', 'Nội dung câu hỏi', 'Trạng thái', 'Ngày gửi'])
    for obj in queryset:
        writer.writerow([obj.id, obj.ho_ten, obj.so_dien_thoai, obj.email, obj.nganh_quan_tam, obj.noi_dung_cau_hoi, obj.get_trang_thai_display(), obj.ngay_gui.strftime('%d/%m/%Y %H:%M')])
    return response
export_tu_van_to_csv.short_description = "Xuất file CSV danh sách đã chọn"


def mark_as_completed(modeladmin, request, queryset):
    queryset.update(trang_thai='da_hoan_thanh', da_tu_van=True)
mark_as_completed.short_description = "Đánh dấu: Đã tư vấn xong"


def mark_as_in_progress(modeladmin, request, queryset):
    queryset.update(trang_thai='dang_tu_van')
mark_as_in_progress.short_description = "Đánh dấu: Đang liên hệ tư vấn"


@admin.register(TuVanTuyenSinh)
class TuVanTuyenSinhAdmin(admin.ModelAdmin):
    list_display = ('ho_ten', 'so_dien_thoai', 'email', 'nganh_quan_tam', 'trang_thai_badge', 'ngay_gui')
    list_filter = ('trang_thai', 'ngay_gui')
    search_fields = ('ho_ten', 'so_dien_thoai', 'email', 'noi_dung_cau_hoi', 'nganh_quan_tam')
    date_hierarchy = 'ngay_gui'
    actions = [export_tu_van_to_csv, mark_as_completed, mark_as_in_progress]
    readonly_fields = ('ngay_gui', 'ngay_cap_nhat')

    def trang_thai_badge(self, obj):
        colors = {
            'cho_xu_ly': '#ea580c',
            'dang_tu_van': '#0284c7',
            'da_hoan_thanh': '#16a34a',
            'huy': '#dc2626',
        }
        color = colors.get(obj.trang_thai, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
            color, obj.get_trang_thai_display()
        )
    trang_thai_badge.short_description = "Trạng thái"
