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
