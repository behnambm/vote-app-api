from django.core.exceptions import ValidationError
from rest_framework import serializers


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class CheckVerificationCodeSerializer(serializers.Serializer):
    code = serializers.CharField()
    email = serializers.EmailField()

    def validate_code(self, value):
        if not value.isdigit():
            raise ValidationError(message="Only digits are allowed")

        if not len(value) == 6:
            raise ValidationError(message="Code is only 6 digits long")

        return value
