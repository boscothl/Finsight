from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from api.models import Claim, BudgetPool
from api.services import ChatbotService
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login
import json
from django.utils import timezone

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
    remaining_budget = sum([p.remaining_hkd for p in pools])
    # For now, simplistic calculation
    total_spend = sum([c.amount_hkd for c in claims if c.status == 'approved' and c.amount_hkd])
    
    # Calculate utilization rate
    utilization_rate = (total_spend / total_budget * 100) if total_budget > 0 else 0
    
    pending_count = Claim.objects.filter(status='pending').count()
    
    # Generate Alerts
    alerts = []
    if utilization_rate > 80:
        alerts.append({'level': 'alert-level-critical', 'message': f'Budget utilization is high ({utilization_rate:.1f}%)'})
    
    if pending_count > 5:
        alerts.append({'level': 'alert-level-warning', 'message': f'{pending_count} claims pending review'})

    # Mock Chart Data (Last 6 Months)
    import random
    chart_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    chart_data = [random.randint(10000, 50000) for _ in range(6)]
    
    # Recent Activity (Mock events for now, could be a real model)
    recent_activity = [
        {'type': 'claim', 'text': 'New claim #1024 from Alice', 'time': timezone.now() - timezone.timedelta(minutes=15)},
        {'type': 'approval', 'text': 'Claim #1023 approved by Admin', 'time': timezone.now() - timezone.timedelta(hours=2)},
        {'type': 'info', 'text': 'Monthly Report Generated', 'time': timezone.now() - timezone.timedelta(days=1)},
    ]

    context = {
        'total_budget': total_budget,
        'total_spend': total_spend,
        'remaining_budget': remaining_budget,
        'utilization_rate': utilization_rate,
        'pending_count': pending_count,
        'claims': claims[:5], # Show latest claims
        'alerts': alerts,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'recent_activity': recent_activity,
        'current_date': timezone.now()
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def chatbot_view(request):
    return render(request, 'chatbot.html')

@login_required(login_url='login')
def approval_view(request):
    pending_claims = Claim.objects.filter(status='pending').order_by('-created_at')
    history_claims = Claim.objects.exclude(status='pending').order_by('-updated_at')[:10]
    
    context = {
        'pending_claims': pending_claims,
        'history_claims': history_claims,
        'pending_count': pending_claims.count()
    }
    return render(request, 'approval.html', context)

@login_required(login_url='login')
def approval_action(request, claim_id, action):
    # Placeholder for approval/rejection logic
    if request.method == "POST":
        try:
            claim = Claim.objects.get(id=claim_id)
            # Capture notes from form
            note = request.POST.get('note')
            if note:
                # Append or set note
                current_note = claim.note or ""
                claim.note = f"{current_note} | Reviewer: {note}"

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
