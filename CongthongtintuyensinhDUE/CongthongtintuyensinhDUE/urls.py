"""
URL configuration for CongthongtintuyensinhDUE project.
"""
from django.contrib import admin
from django.urls import path
from tuyensinh import views as tuyensinh_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('khoa/', views.khoa, name='khoa'),
    path('hoc-phi/', views.hoc_phi, name='hoc_phi'),
    path('career-advisory/', views.career_advisory, name='career_advisory'),
    path('chatbot/', views.chatbot, name='chatbot'),
    
    # API endpoints
    path('api/khoa/<str:code>/', tuyensinh_views.khoa_detail_api, name='api_khoa_detail'),
    path('api/tinh-hoc-phi/', tuyensinh_views.tinh_hoc_phi_api, name='api_tinh_hoc_phi'),
]
