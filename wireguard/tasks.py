import datetime

from celery import shared_task
from django.conf import settings

from telegram_bot import telegram
from telegram_bot.exceptions import TelegramAPIError
from telegram_bot.models import User
from telegram_bot.services import calculate_expiration_time
from wireguard.exceptions import VPNServerError
from wireguard.services import vpn_server
from wireguard.services.queries import group_users_by_server


def get_users_with_expired_subscription(subscription_period: datetime.timedelta):
    now = datetime.datetime.utcnow()
    return (
        User.objects
        .select_related('server')
        .filter(is_subscribed=True, subscribed_at__lte=now - subscription_period)
    )


@shared_task
def expiring_users_notification():
    text = 'У вас заканчивается подписка, вы не сможете пользоваться ВПН. Стоимость продления 300 руб.'
    now = datetime.datetime.utcnow()
    users = User.objects.filter(is_subscribed=True).values('telegram_id', 'subscribed_at', 'is_trial_period')
    for user in users:
        expire_at = calculate_expiration_time(user['subscribed_at'], user['is_trial_period'])
        time_before_expiration = (expire_at - now).total_seconds()
        print(time_before_expiration)
        if (60 * 60 * 24 - 25) <= time_before_expiration <= (60 * 60 * 24 + 25):
            try:
                telegram.send_message(user['telegram_id'], text)
            except TelegramAPIError:
                print(f'Unable to send message to user {user["telegram_id"]}')
        elif (60 * 60 - 25) <= time_before_expiration <= (60 * 60 + 25):
            try:
                telegram.send_message(user['telegram_id'], text)
            except TelegramAPIError:
                print(f'Unable to send message to user {user["telegram_id"]}')


@shared_task
def trial_period_expired_users():
    trial_period_timedelta = datetime.timedelta(days=settings.TRIAL_PERIOD_DAYS)
    users_with_expired_subscription = get_users_with_expired_subscription(trial_period_timedelta)
    server_to_users = group_users_by_server(users_with_expired_subscription)
    users_to_be_updated = []
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
    subscription_period_timedelta = datetime.timedelta(days=settings.SUBSCRIPTION_DAYS)
    users_with_expired_subscription = get_users_with_expired_subscription(subscription_period_timedelta)
    server_to_users = group_users_by_server(users_with_expired_subscription)

    users_to_be_updated = []
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
