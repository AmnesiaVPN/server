import datetime

from celery import shared_task
from django.conf import settings
from django.db.models import Q

from telegram_bot import telegram
from telegram_bot.exceptions import TelegramAPIError
from telegram_bot.models import User
from wireguard.exceptions import VPNServerError
from wireguard.services import vpn_server
from wireguard.services.queries import group_users_by_server


@shared_task
def trial_period_expired_users():
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
                    telegram.send_message(user.telegram_id, 'Пробный период использования закончился. '
                                                            'Продлите подписку чтобы продолжить пользоваться')
                except TelegramAPIError:
                    print(f'Unable to send message to user {user.telegram_id}')

    User.objects.bulk_update(users_to_be_updated, ('is_trial_period', 'is_subscribed'))


@shared_task
def subscription_period_expired_users():
    now = datetime.datetime.utcnow()
    subscription_period_timedelta = datetime.timedelta(days=settings.SUBSCRIPTION_DAYS)
    expired_trial_period_users = (
        User.objects
        .select_related('server')
        .filter(is_subscribed=True, subscribed_at__lte=now - subscription_period_timedelta)
        .all()
    )
    users_to_be_updated = []
    server_to_users = group_users_by_server(expired_trial_period_users)
    for server, users in server_to_users.items():
        with vpn_server.connected_client(server.url, server.password) as client:
            for user in users:
                user.is_subscribed = False
                users_to_be_updated.append(user)

                try:
                    vpn_server.disable_user(client, user.uuid)
                except VPNServerError:
                    print(f'Unable to disable user')

                try:
                    telegram.send_message(user.telegram_id, 'Ваш ваша подписка закончилась')
                except TelegramAPIError:
                    print(f'Unable to send message to user {user.telegram_id}')

    User.objects.bulk_update(users_to_be_updated, ('is_subscribed',))
