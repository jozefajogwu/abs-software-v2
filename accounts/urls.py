from django.urls import path
from .views import SendVerificationCode, VerifyCode

urlpatterns = [
    path('send-code/', SendVerificationCode.as_view(), name='send_code'),
    path('verify-code/', VerifyCode.as_view(), name='verify_code'),
]
