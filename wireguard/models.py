from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Server(models.Model):
    name = models.CharField(max_length=64, unique=True, null=True, blank=True, help_text='Optional')
    url = models.URLField(unique=True, max_length=32)
    password = models.CharField(max_length=255)
    max_users_count = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(100),
        ),
    )

    def __str__(self):
        return self.name or self.url
