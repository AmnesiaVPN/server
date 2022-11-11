from django.db import models


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    is_trial_period = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'User: {self.telegram_id}'
