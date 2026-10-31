"""
URL configuration for CongthongtintuyensinhDUE project.
"""
from django.contrib import admin
from django.urls import path
from tuyensinh import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('khoa/', views.khoa_view, name='khoa'),
    path('hoc-phi/', views.hoc_phi_view, name='hoc_phi'),
    
    # API endpoints
    path('api/khoa/<str:code>/', views.khoa_detail_api, name='api_khoa_detail'),
    path('api/tinh-hoc-phi/', views.tinh_hoc_phi_api, name='api_tinh_hoc_phi'),
]
