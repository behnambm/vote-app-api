from django.db import models


class Emails(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    verified_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.email} (active: {self.is_active})"
