from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from api.models import Claim, BudgetPool
from api.services import ChatbotService
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login
import json

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            return render(request, 'login.html', {'error': 'Please provide both username and password'})
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

@login_required(login_url='login')
def dashboard_view(request):
    # Calculate some stats for the dashboard
    claims = Claim.objects.all()
    pools = BudgetPool.objects.all()
    
    total_budget = sum([p.total_budget_hkd for p in pools])
    # For now, simplistic calculation
    total_spend = sum([c.amount_hkd for c in claims if c.status == 'approved' and c.amount_hkd])
    
    context = {
        'total_budget': total_budget,
        'total_spend': total_spend,
        'claims': claims[:5], # Show latest claims
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def chatbot_view(request):
    return render(request, 'chatbot.html')

@login_required(login_url='login')
def approval_view(request):
    claims = Claim.objects.filter(status='pending').order_by('-created_at')
    return render(request, 'approval.html', {'claims': claims})

@login_required(login_url='login')
def approval_action(request, claim_id, action):
    # Placeholder for approval/rejection logic
    if request.method == "POST":
        try:
            claim = Claim.objects.get(id=claim_id)
            if action == 'approve':
                claim.status = 'approved'
            elif action == 'reject':
                claim.status = 'rejected'
            claim.save()
        except Claim.DoesNotExist:
            pass
    return redirect('approval')

def finance_chat_view(request):
    # This might be called via AJAX so @csrf_exempt might be needed or fetch headers
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            # Call the service
            bot_response = ChatbotService.generate_response(user_message, context="admin")
            return JsonResponse({'response': bot_response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required(login_url='login')
def generate_report_view(request):
    # Placeholder for report generation
    if request.method == "POST":
        report_type = request.POST.get('type', 'pptx')
        # Call proper service to generate file
        # Check permissions, etc.
        # Temp: Return a text file saying report generated
        response = HttpResponse(f"Report generation for {report_type} not implemented yet", content_type="text/plain")
        response['Content-Disposition'] = f'attachment; filename="report.{report_type}.txt"'
        return response
    return redirect('chatbot')
