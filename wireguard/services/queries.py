import collections
from typing import Iterable, DefaultDict

from django.db.models import F, Count

from telegram_bot.exceptions import UserNotFoundError
from telegram_bot.models import User
from wireguard.models import Server
from wireguard.services import vpn_server


def get_server_with_fewer_users() -> Server:
    server = (
        Server.objects
        .annotate(users_count=Count('user__server'))
        .filter(users_count__lt=F('max_users_count'))
        .order_by('users_count')).first()
    if not server:
        raise Server.DoesNotExist('No free servers')
    return server


def group_users_by_server(users: Iterable[User]) -> DefaultDict[Server, list[User]]:
    server_to_users = collections.defaultdict(list)
    for user in users:
        server_to_users[user.server].append(user)
    return server_to_users


def get_user_config(telegram_id: int) -> str:
    user = User.objects.select_related('server').filter(telegram_id=telegram_id).first()
    if not user:
        raise UserNotFoundError
    with vpn_server.connected_client(user.server.url, user.server.password) as client:
        return vpn_server.get_user_config_file(client, user.uuid).text.strip()
