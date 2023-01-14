import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

from wireguard.models import Server


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    uuid = models.UUIDField()
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    is_trial_period = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    subscribed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'User: {self.telegram_id}'

    @property
    def subscription_days_count(self) -> int:
        return settings.TRIAL_PERIOD_DAYS if self.is_trial_period else settings.SUBSCRIPTION_DAYS

    @property
    def is_subscribed(self) -> bool:
        now = timezone.now()
        return now < self.subscription_expires_at

    @property
    def subscription_expires_at(self) -> datetime.datetime:
        return self.subscribed_at + datetime.timedelta(days=self.subscription_days_count)


class ScheduledTask(models.Model):
    uuid = models.UUIDField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
