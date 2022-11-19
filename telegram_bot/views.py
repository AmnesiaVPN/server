from rest_framework.decorators import api_view
from rest_framework.response import Response

from telegram_bot.exceptions import UserAlreadyExistsAPIError
from telegram_bot.serializers import UserCreateSerializer
from telegram_bot.services import get_or_create_user, calculate_expiration_time, get_user_by_telegram_id
from wireguard.exceptions import VPNServerError, NoFreeServersAPIError, VPNServerAPIError
from wireguard.models import Server
from wireguard.services import vpn_server
from wireguard.services.queries import get_server_with_fewer_users


@api_view(['POST'])
def create_user_view(request):
    user_create_serializer = UserCreateSerializer(data=request.data)
    user_create_serializer.is_valid(raise_exception=True)
    telegram_id = user_create_serializer.data['telegram_id']

    try:
        server = get_server_with_fewer_users()
    except Server.DoesNotExist:
        raise NoFreeServersAPIError

    try:
        with vpn_server.connected_client(server.url, server.password) as client:
            user = vpn_server.get_or_create_user(client, str(telegram_id))
    except VPNServerError:
        raise VPNServerAPIError

    user, is_created = get_or_create_user(telegram_id, user.uuid, server)
    if not is_created:
        raise UserAlreadyExistsAPIError

    return Response({
        'telegram_id': telegram_id,
        'is_trial_period': user.is_trial_period,
        'subscribed_at': user.subscribed_at,
        'subscription_expire_at': calculate_expiration_time(user.subscribed_at, user.is_trial_period),
        'is_subscribed': user.is_subscribed,
    })


@api_view(['GET'])
def get_user_view(request, telegram_id: int):
    user = get_user_by_telegram_id(telegram_id)
    return Response({
        'telegram_id': user.telegram_id,
        'is_trial_period': user.is_trial_period,
        'subscribed_at': user.subscribed_at,
        'subscription_expire_at': calculate_expiration_time(user.subscribed_at, user.is_trial_period),
        'is_subscribed': user.is_subscribed,
    })
