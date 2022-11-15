import collections
import datetime
import os
from typing import Iterable, DefaultDict

from django.core.wsgi import get_wsgi_application
from django.conf import settings
from django.db.models import Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vobla_vpn.settings')
application = get_wsgi_application()

from wireguard.exceptions import VPNServerError
from telegram_bot.exceptions import TelegramAPIError
from wireguard.models import Server
from wireguard.services import vpn_server

from telegram_bot.models import User
from telegram_bot import telegram


def group_users_by_server(users: Iterable[User]) -> DefaultDict[Server, list[User]]:
    server_to_users = collections.defaultdict(list)
    for user in users:
        server_to_users[user.server].append(user)
    return server_to_users


def main():
    now = datetime.datetime.utcnow()
    trial_period_timedelta = datetime.timedelta(days=settings.TRIAL_PERIOD_DAYS)
    expired_trial_period_users = (
        User.objects
        .select_related('server')
        .filter(Q(is_trial_period=True) | Q(is_subscribed=True), subscribed_at__lte=now - trial_period_timedelta)
        .all()
    )
    users_to_be_updated = []
    server_to_users = group_users_by_server(expired_trial_period_users)
    for server, users in server_to_users.items():
        with vpn_server.connected_client(server.url, server.password) as client:
            for user in users:
                user.is_trial_period = False
                user.is_subscribed = False
                users_to_be_updated.append(user)

                try:
                    vpn_server.disable_user(client, user.uuid)
                except VPNServerError:
                    print(f'Unable to disable user')

                try:
                    telegram.send_message(user.telegram_id, 'Ваш пробный период истек')
                except TelegramAPIError:
                    print(f'Unable to send message to user {user.telegram_id}')

    User.objects.bulk_update(users_to_be_updated, ('is_trial_period', 'is_subscribed'))


if __name__ == '__main__':
    main()
