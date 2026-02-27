from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('chatbot/', views.chatbot_view, name='chatbot_page'),
    path('chatbot/api/message/', views.finance_chat_view, name='chatbot_message_api'),
    path('approval/', views.approval_view, name='approval'),
]
