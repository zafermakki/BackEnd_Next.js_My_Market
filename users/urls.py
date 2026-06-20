from django.urls import path
from .views import RequestPasswordResetView,VerifyAndResetPasswordView,ResendVerificationEmailView,VerifyCodeView,ClientRegisterView, ClientLoginView, ClientLogoutView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend_verification'),
    path('verify-code/', VerifyCodeView.as_view(), name='verifyCodeView'),
    # client
    path('client/register/', ClientRegisterView.as_view(), name='register'),
    path('client/login/', ClientLoginView.as_view(), name='login'),
    path('client/logout/', ClientLogoutView.as_view(), name='logout'),
    # forget password 
    path('password-reset/', RequestPasswordResetView.as_view(), name='password-reset'),
    path('make-reset/', VerifyAndResetPasswordView.as_view(), name='make-reset'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
]