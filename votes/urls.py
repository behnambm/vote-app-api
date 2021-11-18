from django.urls import path

from .api import VotesView

urlpatterns = [
    path("vote/", VotesView.as_view(), name="vote"),
]
