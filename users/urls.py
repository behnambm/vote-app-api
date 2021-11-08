from django.urls import path

from .api import EmailView

urlpatterns = [
    path('user/email/', EmailView.as_view()),
]
