"""
URL configuration for CongthongtintuyensinhDUE project.
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('career-advisory/', views.career_advisory, name='career_advisory'),
    path('chatbot/', views.chatbot, name='chatbot'),
]
