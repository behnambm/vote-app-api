from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import EmailSerializer
from .utils import (
    generate_verification_code,
    is_code_in_redis,
    set_verification_code,
)


class EmailView(APIView):
    throttle_scope = "email"

    def post(self, request):

        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_email = serializer.data.get("email")

        if is_code_in_redis(user_email):
            return Response(
                {"msg": "please wait  120 seconds"},
                status=status.HTTP_202_ACCEPTED,
            )

        code = generate_verification_code()
        set_verification_code(user_email, code)
        # TODO: use celery to send email
        send_mail(
            "test",
            f"the code is {code}",
            "behnam@gmail.com",
            ["test@gmail.com"],
        )
        return Response({"msg": f"your code {code} -> {user_email}"})
