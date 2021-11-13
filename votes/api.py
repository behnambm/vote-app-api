from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Voters, Votes
from .serializer import VotersSerializer, VotesSerializer


class ListOfVotesView(APIView):
    def get(self, request):
        votes = Votes.objects.all()
        serializer = VotesSerializer(instance=votes, many=True)
        return Response(serializer.data)


class ListOfVotersView(APIView):
    def get(self, request):
        voters = Voters.objects.all()
        serializer = VotersSerializer(instance=voters, many=True)
        return Response(serializer.data)
