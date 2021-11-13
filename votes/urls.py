from django.urls import path

from .api import ListOfVotesView

urlpatterns = [
    path("vote/", ListOfVotesView.as_view()),
]
