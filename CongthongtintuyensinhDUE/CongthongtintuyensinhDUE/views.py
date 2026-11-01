from django.shortcuts import render
# Re-export views from tuyensinh app
from tuyensinh.views import (
    home_view as home,
    khoa_view as khoa,
    hoc_phi_view as hoc_phi,
    enrollment_guide_view as enrollment_guide,
    freshman_schedule_view as freshman_schedule
)

def career_advisory(request):
    return render(request, 'career-advisory.html')

def chatbot(request):
    return render(request, 'chatbot.html')
