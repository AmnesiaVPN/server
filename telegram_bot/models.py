import datetime

from django.db import models
from django.utils import timezone

from wireguard.models import Server


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    uuid = models.UUIDField()
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    is_trial_period = models.BooleanField(default=True)
    is_subscribed = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    subscribed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'User: {self.telegram_id}'

    @property
    def subscription_expires_at(self) -> datetime.datetime:
        subscription_days_count = 3 if self.is_trial_period else 30
        return self.subscribed_at + datetime.timedelta(days=subscription_days_count)
