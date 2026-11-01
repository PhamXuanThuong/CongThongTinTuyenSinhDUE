from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def lich_su_phat_trien(request):
    return render(request, 'lichsuphattrien.html')
