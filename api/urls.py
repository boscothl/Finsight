from django.urls import path
from . import views

urlpatterns = [
    # path('ocr/upload/', views.ocr_upload_view, name='ocr_upload'),
    path('chat/compliance/', views.compliance_chat_view, name='compliance_chat'),
]
