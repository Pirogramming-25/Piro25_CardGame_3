from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    score = models.IntegerField(default=0)
    nickname = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["-score", "-date_joined"]

    def __str__(self):
        return self.username

    @property
    def display_name(self):
        return self.nickname or self.username

    @property
    def win_count(self):
        return self.won_games.count()