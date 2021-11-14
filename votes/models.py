from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.text import slugify
from users.models import Emails


class Votes(models.Model):
    title = models.CharField(max_length=256)
    slug = models.SlugField(blank=True)
    description = models.TextField()
    first_option = models.CharField(max_length=256)
    second_option = models.CharField(max_length=256)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title + f"({self.first_option}, {self.second_option})"


class Voters(models.Model):
    voter = models.ForeignKey(
        to=Emails, related_name="votes", on_delete=models.CASCADE
    )
    vote = models.ForeignKey(
        to=Votes, related_name="voters", on_delete=models.CASCADE
    )
    user_choice = models.CharField(max_length=256)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["voter", "vote"], name="vote_voter_unique_constraint"
            )
        ]

    def __str__(self) -> str:
        return f"{self.voter.email} ({self.user_choice})"
