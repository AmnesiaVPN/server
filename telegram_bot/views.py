from rest_framework.decorators import api_view
from rest_framework.response import Response

from telegram_bot.serializers import UserCreateSerializer
from telegram_bot.services import get_or_create_user, calculate_expiration_time, get_user_by_telegram_id
from telegram_bot.exceptions import UserAlreadyExistsError


@api_view(['POST'])
def create_user_view(request):
    user_create_serializer = UserCreateSerializer(data=request.data)
    user_create_serializer.is_valid(raise_exception=True)
    user, is_created = get_or_create_user(user_create_serializer.data['telegram_id'])
    if not is_created:
        raise UserAlreadyExistsError
    response_data = {
        'telegram_id': user_create_serializer.data['telegram_id'],
        'subscription_expire_at': calculate_expiration_time(user.subscribed_at, user.is_trial_period)
    }
    return Response(response_data)


@api_view(['GET'])
def get_user_view(request, telegram_id: int):
    user = get_user_by_telegram_id(telegram_id)
    response_data = {
        'telegram_id': user.telegram_id,
        'is_trial_period': user.is_trial_period,
        'subscribed_at': user.subscribed_at,
        'subscription_expire_at': calculate_expiration_time(user.subscribed_at, user.is_trial_period),
    }
    return Response(response_data)
