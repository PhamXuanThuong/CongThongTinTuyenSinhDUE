from django.urls import path
from portal import views, api

app_name = 'portal'

urlpatterns = [
    # Khoa & Viện đào tạo (Ưu tiên chuẩn Tiếng Việt người dùng)
    path('khoa/', views.faculty_overview_view, name='khoa'),
    path('khoa/<str:code>/', views.faculty_detail_view, name='khoa_detail'),
    path('khoa/<str:code>/lien-chi-doan/', views.faculty_lcd_detail_view, name='khoa_lcd_detail'),
    path('khoa/<str:code>/lcd/', views.faculty_lcd_detail_view, name='khoa_lcd_detail_short'),

    # Liên Chi Đoàn
    path('lien-chi-doan/', views.lcd_overview_view, name='lien_chi_doan_list'),
    path('lien-chi-doan/<str:code>/', views.faculty_lcd_detail_view, name='lien_chi_doan_detail'),
    path('lcd/', views.lcd_overview_view, name='lcd_list'),
    path('lcd/<str:code>/', views.faculty_lcd_detail_view, name='lcd_detail'),

    # Đời sống sinh viên & Ký túc xá
    path('ky-tuc-xa/', views.dormitory_view, name='ky_tuc_xa'),
    path('ktx/', views.dormitory_view, name='ktx'),
    path('hoat-dong-doan/', views.youth_activity_view, name='hoat_dong_doan'),
    path('doan-thanh-nien/', views.youth_activity_view, name='doan_thanh_nien'),

    # Câu lạc bộ - Đội - Nhóm
    path('clb/', views.club_view, name='clb'),
    path('clb/<str:club_id>/', views.club_detail_view, name='clb_detail'),
    path('cau-lac-bo/', views.club_view, name='cau_lac_bo'),
    path('cau-lac-bo/<str:club_id>/', views.club_detail_view, name='cau_lac_bo_detail'),
    path('sinh-vien/', views.student_life_view, name='sinh_vien'),

    # Hướng dẫn nhập học & Lịch trình tân sinh viên
    path('huong-dan-nhap-hoc/', views.enrollment_guide_view, name='huong_dan_nhap_hoc'),
    path('lich-trinh-tan-sinh-vien/', views.freshman_schedule_view, name='lich_trinh_tan_sinh_vien'),

    # API Endpoints chính thức (Tiếng Việt đồng bộ)
    path('api/khoa/', api.api_faculties_list, name='api_khoa_list'),
    path('api/khoa/<str:code>/', api.api_faculty_detail, name='api_khoa_detail'),
    path('api/clb/', api.api_clubs_list, name='api_clb_list'),
    path('api/clb/dang-ky/', api.api_club_register, name='api_clb_register'),

    # Alias Tiếng Anh phụ trợ (Tùy chọn)
    path('faculties/', views.faculty_overview_view, name='faculties'),
    path('faculties/<str:code>/', views.faculty_detail_view, name='faculty_detail'),
    path('youth-unions/', views.lcd_overview_view, name='youth_unions_list'),
    path('dormitory/', views.dormitory_view, name='dormitory'),
    path('clubs/', views.club_view, name='clubs'),
    path('student-life/', views.student_life_view, name='student_life'),
    path('enrollment-guide/', views.enrollment_guide_view, name='enrollment_guide'),
    path('freshman-schedule/', views.freshman_schedule_view, name='freshman_schedule'),
]
