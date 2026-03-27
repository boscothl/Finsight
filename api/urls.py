from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('mobile/home/', views.MobileHomeView.as_view(), name='mobile_home'),
    path('mobile/budget-pools/', views.MobileBudgetPoolsView.as_view(), name='mobile_budget_pools'),
    path('mobile/claims/', views.MobileClaimsView.as_view(), name='mobile_claims'),
    path('mobile/upload-receipt/', views.MobileUploadReceiptView.as_view(), name='mobile_upload_receipt'),
    
    path('chat/compliance/', views.compliance_chat_view, name='compliance_chat'),
]
