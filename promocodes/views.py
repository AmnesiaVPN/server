from rest_framework.decorators import api_view
from rest_framework.response import Response

from promocodes.serializers import PromocodeSerializer
from promocodes.services import (
    validate_user_and_promocode,
    get_promocode_or_raise_404,
    activate_subscription_via_promocode,
)
from telegram_bot.services import get_user_or_raise_404, calculate_expiration_time


@api_view(['POST'])
def activate_promocode_view(request, telegram_id: int):
    serializer = PromocodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    promocode_value: str = serializer.data['promocode']
    promocode = get_promocode_or_raise_404(promocode_value)
    user = get_user_or_raise_404(telegram_id)
    validate_user_and_promocode(user, promocode)
    user = activate_subscription_via_promocode(user, promocode)
    expire_at = calculate_expiration_time(user.subscribed_at, is_trial_period=False)
    return Response({'expire_at': expire_at})
