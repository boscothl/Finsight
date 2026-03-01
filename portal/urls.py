from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('chat/api/', views.finance_chat_view, name='chat_api'),
    path('approval/', views.approval_view, name='approval'),
    path('approval/action/<int:claim_id>/<str:action>/', views.approval_action, name='approval_action'),
    path('report/generate/', views.generate_report_view, name='generate_report'),
]
