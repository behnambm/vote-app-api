from django.urls import path

from .api import CheckVerificationCodeView, EmailView

urlpatterns = [
    path("user/email/", EmailView.as_view(), name="send-verification-code"),
    path(
        "user/email/check/",
        CheckVerificationCodeView.as_view(),
        name="check-verification-code",
    ),
]
