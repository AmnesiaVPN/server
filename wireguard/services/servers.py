import collections
from typing import Iterable, DefaultDict

from telegram_bot.models import User
from wireguard.models import Server

__all__ = ('group_users_by_server',)


def group_users_by_server(users: Iterable[User]) -> DefaultDict[Server, list[User]]:
    server_to_users = collections.defaultdict(list)
    for user in users:
        server_to_users[user.server].append(user)
    return server_to_users
