from django.core.validators import MinLengthValidator
from django.db import models

from telegram_bot.models import User


class PromocodesGroup(models.Model):
    name = models.CharField(max_length=64)
    expire_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_count(self):
        return self.promocode_set.count()


class Promocode(models.Model):
    value = models.CharField(max_length=8, unique=True, validators=(MinLengthValidator(8),))
    group = models.ForeignKey(PromocodesGroup, on_delete=models.CASCADE)
    activated_at = models.DateTimeField(null=True, blank=True)
    activated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.value
