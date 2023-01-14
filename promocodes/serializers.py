from rest_framework import serializers


class PromocodeSerializer(serializers.Serializer):
    promocode = serializers.CharField(max_length=8, min_length=8)
