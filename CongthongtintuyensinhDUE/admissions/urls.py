from django.urls import path
from . import views

app_name = 'admissions'

urlpatterns = [
    # Trang giao diện chính
    path('', views.home_view, name='home'),
    path('lich-su-phat-trien/', views.history_view, name='history'),
    path('su-menh-tam-nhin/', views.mission_vision_view, name='mission_vision'),
    path('phuong-thuc-xet-tuyen/', views.admission_methods_view, name='admission_methods'),
    path('diem-chuan-cac-nam/', views.benchmarks_view, name='benchmarks'),
    path('chi-tieu-tuyen-sinh/', views.admission_quota_view, name='admission_quota'),
    path('loai-hinh-dao-tao/', views.training_programs_view, name='training_programs'),
    path('hoc-phi/', views.tuition_fees_view, name='tuition_fees'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('huong-nghiep/', views.career_advisory_view, name='career_advisory'),

    # Xác thực người dùng (Đăng nhập & Đăng xuất)
    path('dang-nhap/', views.login_view, name='login'),
    path('dang-xuat/', views.logout_view, name='logout'),

    # Form đăng ký tư vấn tuyển sinh
    path('dang-ky-tu-van/', views.counseling_request_view, name='counseling_request'),
    
    # Chi tiết bài viết tin tức
    path('tin-tuc/<slug:slug>/', views.news_detail_view, name='news_detail'),
    
    # Các API Endpoints
    path('api/tra-cuu/', views.api_search_majors, name='api_search_majors'),
    path('api/chatbot/', views.api_chatbot_legacy, name='api_chatbot_legacy'),
    path('api/chat/', views.api_chat, name='api_chat'),
    path('api/thong-ke/', views.api_statistics, name='api_statistics'),
    path('api/tu-van-huong-nghiep/', views.api_career_advisory, name='api_career_advisory'),
    path('api/tinh-hoc-phi/', views.api_calculate_tuition, name='api_calculate_tuition'),
    path('api/tailieu/', views.api_documents_list, name='api_documents_list'),
    path('api/tailieu/upload/', views.api_documents_upload, name='api_documents_upload'),
    path('api/tailieu/<int:doc_id>/delete/', views.api_documents_delete, name='api_documents_delete'),
    path('api/chat/updates/', views.api_chat_updates, name='api_chat_updates'),

    # Quản lý phiên chat và lịch sử hội thoại
    path('api/chat/sessions/', views.api_chat_sessions, name='api_chat_sessions'),
    path('api/chat/sessions/<str:session_id>/', views.api_chat_session_detail, name='api_chat_session_detail'),
    path('api/chat/sessions/<str:session_id>/delete/', views.api_chat_session_delete, name='api_chat_session_delete'),

    # Cán bộ tuyển sinh trả lời câu hỏi Chatbot chuyển tới
    path('can-bo/hoi-dap/', views.officer_qa_view, name='officer_qa'),
    path('api/can-bo/cau-hoi/', views.api_officer_questions, name='api_officer_questions'),
    path('api/can-bo/cau-hoi/<int:q_id>/tra-loi/', views.api_officer_reply, name='api_officer_reply'),
    path('api/can-bo/cau-hoi/<int:q_id>/delete/', views.api_officer_delete, name='api_officer_delete'),
]
