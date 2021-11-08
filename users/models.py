from django.db import models


class Emails(models.Model):
    email = models.EmailField(unique=True)
    verify_key = models.CharField(max_length=256, blank=True, default=None)
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.email + '(' + self.verify_key + ')'
