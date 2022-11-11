from rest_framework import serializers

from telegram_bot.models import User


class UserCreateSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
