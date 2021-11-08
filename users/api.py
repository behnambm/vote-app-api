from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail

from .serializer import EmailSerializer


class EmailView(APIView):
    throttle_scope = 'email'

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO: generate verification code 
        # TODO: save the code in redis
        # TODO: use celery to send email
        send_mail('test', 'the code is 34534', 'behnam@gmail.com', ['test@gmail.com'])
        return Response({'msg': 'check your inbox'})

