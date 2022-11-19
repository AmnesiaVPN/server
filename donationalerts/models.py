from django.db import models

from telegram_bot.models import User


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    donation_id = models.BigIntegerField(unique=True, db_index=True)
    created_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
