from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task(bind=True)
def send_verification_code(self, email: str, code: str) -> None:
    """send emails containing verification code

    Args:
        email (str): destination email address
        code (str): verification code

    Raises:
        self.retry: if any error occurs Celery will re-try to send email

    Returns:
        [int]: number of email being sent. in this case it will be 1
    """
    try:
        return send_mail(
            subject="Verification Code",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            message=f"Your verification code is {code}",
            html_message=render_to_string("email.html", {"code": code}),
        )
    except Exception as e:
        # TODO: log errors
        raise self.retry(exc=e, countdown=5)
