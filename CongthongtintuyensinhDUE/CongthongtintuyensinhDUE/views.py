from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def career_advisory(request):
    return render(request, 'career-advisory.html')

def chatbot(request):
    return render(request, 'chatbot.html')
