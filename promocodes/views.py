from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from promocodes.selectors import get_promocode
from promocodes.services import PromocodeValidator, activate_subscription_via_promocode
from telegram_bot.selectors import get_user


class PromocodeActivateApi(APIView):
    class InputSerializer(serializers.Serializer):
        promocode = serializers.CharField(min_length=8, max_length=8)

    class OutputSerializer(serializers.Serializer):
        subscription_expires_at = serializers.DateTimeField()

    def post(self, request, telegram_id: int):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        promocode_value: str = serializer.data['promocode'].upper()

        promocode = get_promocode(value=promocode_value, include_group=True)
        user = get_user(telegram_id=telegram_id)

        promocode_validator = PromocodeValidator(user=user, promocode=promocode)
        promocode_validator.validate()
        activate_subscription_via_promocode(user=user, promocode=promocode)

        serializer = self.OutputSerializer(user)
        return Response(serializer.data)
