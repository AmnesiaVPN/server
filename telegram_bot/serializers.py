from rest_framework import serializers


class UserCreateSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
