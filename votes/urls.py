from django.urls import path

from .api import ListOfVotersView, ListOfVotesView

urlpatterns = [
    path("vote/", ListOfVotesView.as_view()),
    path("voter/", ListOfVotersView.as_view()),
]
