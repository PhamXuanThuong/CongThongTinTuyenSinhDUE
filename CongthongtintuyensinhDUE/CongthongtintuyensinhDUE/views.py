import json
import os
import unicodedata
import re
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
# Re-export views from tuyensinh app
from tuyensinh.views import home_view as home, hoc_phi_view as hoc_phi

def home(request):
    return render(request, 'home.html')

def lich_su_phat_trien(request):
    return render(request, 'lichsuphattrien.html')
