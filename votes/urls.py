from django.urls import path

from .api import ListOfVotersView, VotesView

urlpatterns = [
    path("vote/", VotesView.as_view()),
    path("voter/", ListOfVotersView.as_view()),
]
