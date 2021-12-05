from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Emails

from .models import Voters, Votes
from .permission import ActiveEmailOnly
from .serializer import VotesSerializer, VoteUpdateSerializer


class VotesView(APIView):
    permission_classes = [ActiveEmailOnly]

    @swagger_auto_schema(
        operation_id="Get list of votes",
        operation_description=f"""
        Get list of votes 
        """,
        responses={
            200: openapi.Response(
                description="ok",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "title": "cats vs dogs",
                            "slug": "cats-vs-dogs",
                            "description": "test vote",
                            "first_option": "cats",
                            "second_option": "dogs",
                        },
                    ]
                },
            ),
        },
        security=[],
    )
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

    @swagger_auto_schema(
        operation_id="Insert or Update vote",
        operation_description=f"""
        Users can update/insert their vote.
        """,
        request_body=VoteUpdateSerializer,
        responses={
            200: openapi.Response(
                description="ok",
                examples={
                    "application/json": {
                        "detail": "successful",
                        "user_choice": "cats",
                    }
                },
            ),
            404: openapi.Response(
                description="vote does not exist",
                examples={
                    "application/json": {"detail": "vote does not exist"}
                },
            ),
            400: openapi.Response(
                description="wrong user choice",
                examples={
                    "application/json": {
                        "detail": "'fox' is not a valid option",
                        "valid_options": ["cats", "dogs"],
                    }
                },
            ),
        },
        security=[],
    )
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
                voter=email_obj,
                vote=user_vote,
                user_choice=serializer.data.get("user_choice"),
            )
        voter.save()

        return Response(
            {
                "detail": "successful",
                "user_choice": serializer.data.get("user_choice"),
            }
        )
