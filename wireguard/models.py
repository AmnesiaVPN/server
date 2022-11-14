from django.db import models


class Server(models.Model):
    url = models.CharField(unique=True, max_length=32)
    password = models.CharField(max_length=255)
    max_users_count = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.url
