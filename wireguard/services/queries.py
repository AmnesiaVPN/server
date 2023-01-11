import collections
from typing import Iterable, DefaultDict

from django.db.models import F, Count

from telegram_bot.models import User
from wireguard.models import Server


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
