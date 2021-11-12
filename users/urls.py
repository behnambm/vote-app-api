from django.urls import path

from .api import CheckVerificationCodeView, EmailView

urlpatterns = [
    path("user/email/", EmailView.as_view()),
    path("user/email/check/", CheckVerificationCodeView.as_view()),
]
