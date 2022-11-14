from typing import Iterable

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from telegram_bot.exceptions import UserAlreadyExistsError
from telegram_bot.serializers import UserCreateSerializer
from telegram_bot.services import get_or_create_user, calculate_expiration_time, get_user_by_telegram_id
from wireguard import schemas
from wireguard.exceptions import NotFoundInCollectionError
from wireguard.models import Server
from wireguard.services import vpn_server
from wireguard.services.queries import get_server_with_fewer_users


def find_user_by_name(users: Iterable[schemas.User], name: str) -> schemas.User:
    try:
        return [user for user in users if user.name == str(name)][0]
    except IndexError:
        raise NotFoundInCollectionError


@api_view(['POST'])
def create_user_view(request):
    user_create_serializer = UserCreateSerializer(data=request.data)
    user_create_serializer.is_valid(raise_exception=True)
    telegram_id = user_create_serializer.data['telegram_id']

    try:
        server = get_server_with_fewer_users()
    except Server.DoesNotExist:
        raise APIException(detail='No free servers', code=status.HTTP_507_INSUFFICIENT_STORAGE)

    with vpn_server.connected_client(server.url, server.password) as client:
        users = vpn_server.get_all_users(client)
        try:
            user = find_user_by_name(users, name=str(telegram_id))
        except NotFoundInCollectionError:
            vpn_server.create_user(client, name=str(telegram_id))
            user = find_user_by_name(vpn_server.get_all_users(client), name=str(telegram_id))

    user, is_created = get_or_create_user(telegram_id, user.uuid, server)
    if not is_created:
        raise UserAlreadyExistsError

    response_data = {
        'telegram_id': user_create_serializer.data['telegram_id'],
        'is_trial_period': user.is_trial_period,
        'subscribed_at': user.subscribed_at,
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
