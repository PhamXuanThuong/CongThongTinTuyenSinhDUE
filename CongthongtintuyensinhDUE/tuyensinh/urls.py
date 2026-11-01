from django.urls import path
from . import views

app_name = 'tuyensinh'

urlpatterns = [
    # Các trang giao diện chính
    path('', views.home, name='home'),
    path('lich-su-phat-trien/', views.lich_su_phat_trien, name='lich_su_phat_trien'),
    path('su-mang-tam-nhin/', views.su_mang_tam_nhin, name='su_mang_tam_nhin'),
    path('su-menh-tam-nhin/', views.su_mang_tam_nhin, name='su_menh_tam_nhin'),
    path('phuong-thuc-xet-tuyen/', views.phuong_thuc_xet_tuyen, name='phuong_thuc_xet_tuyen'),
    path('diem-chuan-cac-nam/', views.diem_chuan_cac_nam, name='diem_chuan_cac_nam'),
    path('chi-tieu-tuyen-sinh/', views.chi_tieu_tuyen_sinh, name='chi_tieu_tuyen_sinh'),
    path('loai-hinh-dao-tao/', views.loai_hinh_dao_tao, name='loai_hinh_dao_tao'),
    
    # Xác thực người dùng (Đăng nhập & Đăng xuất)
    path('dang-nhap/', views.dang_nhap, name='dang_nhap'),
    path('dang-xuat/', views.dang_xuat, name='dang_xuat'),

    # Form đăng ký tư vấn
    path('dang-ky-tu-van/', views.dang_ky_tu_van, name='dang_ky_tu_van'),
    
    # Chi tiết bài viết tin tức
    path('tin-tuc/<slug:slug>/', views.chi_tiet_tin_tuc, name='chi_tiet_tin_tuc'),
    
    # Các API Endpoints
    path('api/tra-cuu/', views.api_tra_cuu_nganh, name='api_tra_cuu_nganh'),
    path('api/chatbot/', views.api_chatbot, name='api_chatbot'),
    path('api/thong-ke/', views.api_thong_ke, name='api_thong_ke'),
    path('api/tu-van-huong-nghiep/', views.api_tu_van_huong_nghiep, name='api_tu_van_huong_nghiep'),
    path('api/clb/dang-ky/', views.api_dang_ky_clb, name='api_dang_ky_clb'),
]
