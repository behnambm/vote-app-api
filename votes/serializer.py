from rest_framework import serializers

from .models import Voters, Votes


class VotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Votes
        fields = "__all__"


class VotersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voters
        fields = "__all__"


class VoteUpdateSerializer(serializers.Serializer):
    """serializer to check data that client is providing

    Args:
        serializers (rest_framework.serializers.Serializer): To inherit
        all serializers attributes
    """

    email = serializers.EmailField()
    user_choice = serializers.CharField()
    vote_id = serializers.IntegerField()
