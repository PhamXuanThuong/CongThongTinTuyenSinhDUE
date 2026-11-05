from django.urls import path
from . import views

app_name = 'admissions'

urlpatterns = [
    # Trang giao diện chính (Chuẩn Tiếng Việt đồng bộ 100%)
    path('', views.home, name='home'),
    path('lich-su-phat-trien/', views.lich_su_phat_trien, name='lich_su_phat_trien'),
    path('su-mang-tam-nhin/', views.su_mang_tam_nhin, name='su_mang_tam_nhin'),
    path('su-menh-tam-nhin/', views.su_mang_tam_nhin, name='su_menh_tam_nhin'),
    path('phuong-thuc-xet-tuyen/', views.phuong_thuc_xet_tuyen, name='phuong_thuc_xet_tuyen'),
    path('diem-chuan-cac-nam/', views.diem_chuan_cac_nam, name='diem_chuan_cac_nam'),
    path('chi-tieu-tuyen-sinh/', views.chi_tieu_tuyen_sinh, name='chi_tieu_tuyen_sinh'),
    path('loai-hinh-dao-tao/', views.loai_hinh_dao_tao, name='loai_hinh_dao_tao'),
    path('hoc-phi/', views.hoc_phi_view, name='hoc_phi'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('huong-nghiep/', views.career_advisory_view, name='huong_nghiep'),
    path('career-advisory/', views.career_advisory_view, name='career_advisory'),

    # Xác thực người dùng (Đăng nhập & Đăng xuất)
    path('dang-nhap/', views.dang_nhap, name='dang_nhap'),
    path('dang-xuat/', views.dang_xuat, name='dang_xuat'),

    # Form đăng ký tư vấn tuyển sinh
    path('dang-ky-tu-van/', views.dang_ky_tu_van, name='dang_ky_tu_van'),
    
    # Chi tiết bài viết tin tức
    path('tin-tuc/<slug:slug>/', views.chi_tiet_tin_tuc, name='chi_tiet_tin_tuc'),
    
    # Các API Endpoints chính thức (Tiếng Việt đồng bộ)
    path('api/tra-cuu/', views.api_tra_cuu_nganh, name='api_tra_cuu_nganh'),
    path('api/chatbot/', views.api_chatbot, name='api_chatbot'),
    path('api/chat/', views.chat_api, name='api_chat'),
    path('api/thong-ke/', views.api_thong_ke, name='api_thong_ke'),
    path('api/tu-van-huong-nghiep/', views.api_tu_van_huong_nghiep, name='api_tu_van_huong_nghiep'),
    path('api/tinh-hoc-phi/', views.tinh_hoc_phi_api, name='api_tinh_hoc_phi'),
    path('api/tailieu/', views.tailieu_list_api, name='api_tailieu_list'),
    path('api/tailieu/upload/', views.tailieu_upload_api, name='api_tailieu_upload'),
    path('api/tailieu/<int:doc_id>/delete/', views.tailieu_delete_api, name='api_tailieu_delete'),
    path('api/chat/updates/', views.chat_updates_api, name='api_chat_updates'),

    # Cán bộ tuyển sinh trả lời câu hỏi Chatbot chuyển tới
    path('can-bo/hoi-dap/', views.can_bo_hoi_dap_view, name='can_bo_hoi_dap'),
    path('api/can-bo/cau-hoi/', views.can_bo_cau_hoi_api, name='api_can_bo_cau_hoi'),
    path('api/can-bo/cau-hoi/<int:q_id>/tra-loi/', views.can_bo_tra_loi_api, name='api_can_bo_tra_loi'),

    # Alias Tiếng Anh phụ trợ (Tùy chọn)
    path('history/', views.lich_su_phat_trien, name='history'),
    path('mission-vision/', views.su_mang_tam_nhin, name='mission_vision'),
    path('admission-methods/', views.phuong_thuc_xet_tuyen, name='admission_methods'),
    path('benchmarks/', views.diem_chuan_cac_nam, name='benchmarks'),
    path('admission-quota/', views.chi_tieu_tuyen_sinh, name='admission_quota'),
    path('training-programs/', views.loai_hinh_dao_tao, name='training_programs'),
    path('tuition-fees/', views.hoc_phi_view, name='tuition_fees'),
    path('login/', views.dang_nhap, name='login'),
    path('logout/', views.dang_xuat, name='logout'),
]
