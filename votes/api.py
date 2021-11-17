from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Emails

from .models import Voters, Votes
from .permission import ActiveEmailOnly
from .serializer import VotesSerializer, VoteUpdateSerializer


class VotesView(APIView):
    permission_classes = [ActiveEmailOnly]

    def get(self, request):
        """Get list of votes

        Args:
            request (django.request): django request object

        Returns:
            rest_framework.response.Response: list of all votes in Json format
        """
        votes = Votes.objects.all()
        serializer = VotesSerializer(instance=votes, many=True)
        return Response(serializer.data)

    def put(self, request):
        """update if already exists or add new data to `votes.models.Voters`

        Args:
            request (django.request): django request object

        Returns:
            rest_framework.response.Response: successful | 404 | 400
        """
        serializer = VoteUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            email_obj = Emails.objects.get(email=serializer.data.get("email"))
        except Emails.DoesNotExist:
            return Response(
                {"detail": "email not found"}, status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, email_obj)

        try:
            user_vote = Votes.objects.get(id=serializer.data.get("vote_id"))
            ALLOWED_CHOICES = [
                user_vote.first_option,
                user_vote.second_option,
            ]
        except Votes.DoesNotExist:
            return Response(
                {"detail": "vote does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not serializer.data.get("user_choice") in ALLOWED_CHOICES:
            return Response(
                {
                    "detail": f"{serializer.data.get('user_choice')!r} is not a valid option",
                    "valid_options": ALLOWED_CHOICES,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            voter = Voters.objects.get(Q(voter=email_obj) & Q(vote=user_vote))
            voter.user_choice = serializer.data.get("user_choice")
        except Voters.DoesNotExist:
            voter = Voters(
                voter=email_obj.id,
                vote=user_vote,
                user_choice=serializer.data.get("user_choice"),
            )
        voter.save()

        return Response({"detail": "successful"})
