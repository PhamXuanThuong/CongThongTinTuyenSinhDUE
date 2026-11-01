"""
URL configuration for CongthongtintuyensinhDUE project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tuyensinh import views as tuyensinh_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Tuyển sinh app routes (home, auth, giới thiệu, phương thức, điểm chuẩn, chỉ tiêu, loại hình, api)
    path('', include('tuyensinh.urls')),

    # Khoa & Đơn vị đào tạo 2026 (từ nhánh main)
    path('khoa/', views.khoa_overview_view, name='khoa'),
    path('khoa/<str:code>/', views.khoa_detail_view, name='khoa_detail'),
    path('khoa/<str:code>/lien-chi-doan/', views.lien_chi_doan_detail_view, name='khoa_lcd_detail'),
    path('khoa/<str:code>/lcd/', views.lien_chi_doan_detail_view, name='khoa_lcd_detail_short'),

    # Liên Chi Đoàn riêng biệt (từ nhánh main)
    path('lien-chi-doan/', views.lien_chi_doan_overview_view, name='lien_chi_doan_list'),
    path('lien-chi-doan/<str:code>/', views.lien_chi_doan_detail_view, name='lien_chi_doan_detail'),
    path('lcd/', views.lien_chi_doan_overview_view, name='lcd_list'),
    path('lcd/<str:code>/', views.lien_chi_doan_detail_view, name='lcd_detail'),

    # Học phí (từ nhánh main)
    path('hoc-phi/', tuyensinh_views.hoc_phi_view, name='hoc_phi'),
    path('api/tinh-hoc-phi/', tuyensinh_views.tinh_hoc_phi_api, name='api_tinh_hoc_phi'),

    # Hướng nghiệp & Chatbot (từ nhánh main)
    path('career-advisory/', views.career_advisory, name='career_advisory'),
    path('chatbot/', views.chatbot, name='chatbot'),

    # Dành cho sinh viên & Tiện ích nội trú (từ nhánh main)
    path('ky-tuc-xa/', views.ky_tuc_xa_view, name='ky_tuc_xa'),
    path('ktx/', views.ky_tuc_xa_view, name='ktx'),
    path('hoat-dong-doan/', views.hoat_dong_doan_view, name='hoat_dong_doan'),
    path('doan-thanh-nien/', views.hoat_dong_doan_view, name='doan_thanh_nien'),

    # Câu lạc bộ & Dành cho sinh viên (từ nhánh main)
    path('clb/', views.clb_view, name='clb'),
    path('clb/<str:club_id>/', views.clb_detail_view, name='clb_detail'),
    path('cau-lac-bo/', views.clb_view, name='cau_lac_bo'),
    path('cau-lac-bo/<str:club_id>/', views.clb_detail_view, name='cau_lac_bo_detail'),
    path('sinh-vien/', views.sinh_vien_view, name='sinh_vien'),

    # API endpoints (từ nhánh main)
    path('api/khoa/', views.api_khoa_list, name='api_khoa_list'),
    path('api/khoa/<str:code>/', views.api_khoa_detail, name='api_khoa_detail'),
    path('api/clb/', views.api_clb_list, name='api_clb_list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
