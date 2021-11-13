from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Votes
from .serializer import VotesSerializer


class ListOfVotesView(APIView):
    def get(self, request):
        votes = Votes.objects.all()
        serializer = VotesSerializer(instance=votes, many=True)
        return Response(serializer.data)

