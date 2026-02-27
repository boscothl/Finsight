from django.shortcuts import render

def login_view(request):
    return render(request, 'login.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def chatbot_view(request):
    return render(request, 'chatbot.html')

def approval_view(request):
    return render(request, 'approval.html')
