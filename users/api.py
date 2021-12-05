from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Emails
from .serializer import CheckVerificationCodeSerializer, EmailSerializer
from .tasks import send_verification_code
from .utils import (generate_verification_code, is_code_correct,
                    is_code_in_redis, set_verification_code)


class EmailView(APIView):
    throttle_scope = "email"

    @swagger_auto_schema(
        operation_id="Send verification code",
        operation_description=f"""
        Sends an email containing 6-digit verification code 
        """,
        request_body=EmailSerializer,
        responses={
            200: openapi.Response(
                description="ok",
                examples={
                    "application/json": {
                        "detail": f"please check your inbox at 'user@example.com'"
                    }
                },
            ),
            202: openapi.Response(
                description=f"wait {settings.VERIFICATION_CODE_EXPIRY} seconds",
                examples={
                    "application/json": {
                        "detail": f"please wait {settings.VERIFICATION_CODE_EXPIRY} seconds"
                    }
                },
            ),
            400: openapi.Response(
                description="invalid email",
                examples={
                    "application/json": {
                        "email": ["Enter a valid email address."]
                    }
                },
            ),
        },
        security=[],
    )
    def post(self, request):

        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_email = serializer.data.get("email")

        if is_code_in_redis(user_email):
            return Response(
                {"detail": "please wait 120 seconds"},
                status=status.HTTP_202_ACCEPTED,
            )

        code = generate_verification_code()
        set_verification_code(user_email, code)
        send_verification_code.delay(email=user_email, code=code)

        return Response(
            {"detail": f"please check your inbox at {user_email!r}"}
        )


class CheckVerificationCodeView(APIView):
    throttle_scope = "email"

    def post(self, request):
        serializer = CheckVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not is_code_correct(
            email=serializer.data.get("email"),
            user_provided_code=serializer.data.get("code"),
        ):
            return Response(
                {"detail": "Code is not correct"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email_obj, _ = Emails.objects.get_or_create(
            email=serializer.data.get("email")
        )
        email_obj.is_active = True
        email_obj.save()

        return Response({"detail": "successful"})
