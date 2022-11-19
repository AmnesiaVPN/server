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


def get_users_with_expired_subscription(subscription_period: datetime.timedelta, is_trial_period: bool):
    now = datetime.datetime.utcnow()
    return (
        User.objects
        .select_related('server')
        .filter(is_subscribed=True, is_trial_period=is_trial_period, subscribed_at__lte=now - subscription_period)
    )


@shared_task
def expiring_users_notification():
    markup = telegram.get_payment_page_markup()
    now = datetime.datetime.utcnow()
    users = User.objects.filter(is_subscribed=True).values('telegram_id', 'subscribed_at', 'is_trial_period')
    for user in users:
        expire_at = calculate_expiration_time(user['subscribed_at'], user['is_trial_period'])
        time_before_expiration = (expire_at - now).total_seconds()
        if (60 * 60 * 24 - 25) <= time_before_expiration <= (60 * 60 * 24 + 25):
            try:
                telegram.send_message(user['telegram_id'], 'Ваша подписка заканчивается через 24 часа.'
                                                           ' Стоимость продления 299 рублей.'
                                                           '\nВажно❗️'
                                                           f'\nПри оплате в комментарии укажите имя вашего файла <b>{user.telegram_id}</b>',
                                      markup)

            except TelegramAPIError:
                print(f'Unable to send message to user {user["telegram_id"]}')
        elif (60 * 60 - 25) <= time_before_expiration <= (60 * 60 + 25):
            try:
                telegram.send_message(user['telegram_id'], 'Ваша подписка заканчивается через 1 час.'
                                                           ' Стоимость продления 299 рублей.'
                                                           '\nВажно❗️'
                                                           f'\nПри оплате в комментарии укажите имя вашего файла <b>{user.telegram_id}</b>',
                                      markup)
            except TelegramAPIError:
                print(f'Unable to send message to user {user["telegram_id"]}')


@shared_task
def trial_period_expired_users():
    markup = telegram.get_payment_page_markup()
    trial_period_timedelta = datetime.timedelta(days=settings.TRIAL_PERIOD_DAYS)
    users_with_expired_subscription = get_users_with_expired_subscription(trial_period_timedelta, is_trial_period=True)
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
                    telegram.send_message(user.telegram_id, 'Пробный период использования закончился.'
                                                            ' Продлите подписку чтобы продолжить пользоваться.'
                                                            ' Стоимость продления 299 рублей'
                                                            '\nВажно❗️'
                                                            f'\nПри оплате в комментарии укажите имя вашего файла <b>{user.telegram_id}</b>',
                                          markup)
                except TelegramAPIError:
                    print(f'Unable to send message to user {user.telegram_id}')

    User.objects.bulk_update(users_to_be_updated, ('is_trial_period', 'is_subscribed'))


@shared_task
def subscription_period_expired_users():
    markup = telegram.get_payment_page_markup()
    subscription_period_timedelta = datetime.timedelta(days=settings.SUBSCRIPTION_DAYS)
    users_with_expired_subscription = get_users_with_expired_subscription(subscription_period_timedelta,
                                                                          is_trial_period=False)
    server_to_users = group_users_by_server(users_with_expired_subscription)

    users_to_be_updated = []
    for server, users in server_to_users.items():
        with vpn_server.connected_client(server.url, server.password) as client:
            for user in users:
                print(user)
                user.is_subscribed = False
                users_to_be_updated.append(user)

                try:
                    vpn_server.disable_user(client, user.uuid)
                except VPNServerError:
                    print(f'Unable to disable user')

                try:
                    telegram.send_message(user.telegram_id, 'Ваша подписка закончилась.'
                                                            ' Вы отключены от VPN. Стоимость продления 299 рублей'
                                                            '\nВажно❗️'
                                                            f'\nПри оплате в комментарии укажите имя вашего файла <b>{user.telegram_id}</b>',
                                          markup)

                except TelegramAPIError:
                    print(f'Unable to send message to user {user.telegram_id}')

    User.objects.bulk_update(users_to_be_updated, ('is_subscribed',))
