from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from api.models import Claim, BudgetPool, ChatSession, ChatMessage, GeneratedReport
from api.services import ChatbotService, ReportGenerationService
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth import authenticate, login
from django.conf import settings
from google.cloud import storage
import json
import urllib.parse
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
    # Fetch or create a chat session for report generation
    session, created = ChatSession.objects.get_or_create(
        user=request.user, 
        context="report_builder"
    )
    # Get chat history
    messages = session.messages.order_by('timestamp')
    
    return render(request, 'chatbot.html', {
        'chat_messages': messages
    })

@login_required(login_url='login')
def reports_view(request):
    reports = GeneratedReport.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'reports.html', {'reports': reports})

@login_required(login_url='login')
def download_report(request, report_id):
    try:
        report = GeneratedReport.objects.get(id=report_id)
        if report.user != request.user:
            raise Http404("Report not found")

        prefix = f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/"
        if not report.file_url.startswith(prefix):
            raise Http404("Invalid blob format")
            
        blob_name = urllib.parse.unquote(report.file_url[len(prefix):])

        client = storage.Client()
        bucket = client.bucket(settings.GS_BUCKET_NAME)
        blob = bucket.blob(blob_name)
        
        file_bytes = blob.download_as_bytes()

        content_type = 'application/octet-stream'
        if '.xlsx' in blob_name:
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif '.docx' in blob_name:
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif '.pptx' in blob_name:
            content_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'

        response = HttpResponse(file_bytes, content_type=content_type)
        
        clean_filename = blob_name.split('_', 1)[-1] if '_' in blob_name else blob_name.split('/')[-1]
        response['Content-Disposition'] = f'attachment; filename="{clean_filename}"'
        
        return response
        
    except GeneratedReport.DoesNotExist:
        raise Http404("Report not found")

@login_required(login_url='login')
def create_budget_pool(request):
    if request.method == "POST":
        name = request.POST.get('name')
        group = request.POST.get('group')
        amount = request.POST.get('amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if not all([name, amount, start_date, end_date]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        try:
            budget_pool = BudgetPool.objects.create(
                company=request.user.company,
                name=name,
                group=group,
                total_budget_hkd=amount,
                remaining_hkd=amount,
                start_date=start_date,
                end_date=end_date
            )
            return JsonResponse({'success': True, 'id': budget_pool.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=405)

@login_required(login_url='login')
def approval_view(request):
    budget_pools = BudgetPool.objects.all()
    pending_claims = Claim.objects.filter(status='pending').order_by('-created_at')
    history_claims = Claim.objects.exclude(status='pending').order_by('-updated_at')[:10]
    
    context = {
        'budget_pools': budget_pools,
        'pending_claims': pending_claims,
        'history_claims': history_claims,
        'pending_count': pending_claims.count()
    }
    return render(request, 'approval.html', context)

@login_required(login_url='login')
def approval_action(request, claim_id, action):
    # Approval/rejection logic
    if request.method == "POST":
        try:
            from api.models import Approval
            claim = Claim.objects.get(id=claim_id)
            # Capture notes from form
            note = request.POST.get('note')
            
            # Create Approval record
            approval = Approval.objects.create(
                claim=claim,
                approver=request.user,
                decision=action,
                comment=note if note else ""
            )

            if action == 'approve':
                claim.status = 'approved'
            elif action == 'reject':
                claim.status = 'rejected'
            
            claim.save()
        except Claim.DoesNotExist:
            pass
    return redirect('approval')

@login_required(login_url='login')
def finance_chat_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message_text = data.get('message', '').strip()
            if not user_message_text:
                return JsonResponse({'error': 'Empty message'}, status=400)

            # Get the session
            session, _ = ChatSession.objects.get_or_create(user=request.user, context="report_builder")
            
            # Save user message to DB
            ChatMessage.objects.create(session=session, role="user", content=user_message_text)

            # Pass the session ID to the service so it can read history
            bot_response = ChatbotService.generate_report_chat_response(session, user_message_text)
            
            # Save bot message to DB
            ChatMessage.objects.create(session=session, role="model", content=bot_response)

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
