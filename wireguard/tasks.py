import datetime
import logging

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.db.models import Q

from telegram_bot import telegram
from telegram_bot.models import User
from telegram_bot.services import calculate_expiration_time
from wireguard.services import vpn_server
from wireguard.services.queries import group_users_by_server


@shared_task
def subscription_control():
    markup = telegram.get_payment_page_markup()
    now = datetime.datetime.utcnow()
    trial_period_should_have_started_at = now - datetime.timedelta(days=settings.TRIAL_PERIOD_DAYS)
    subscription_should_have_started_at = now - datetime.timedelta(days=settings.SUBSCRIPTION_DAYS)
    expiring_users = (
        User.objects
        .select_related('server')
        .prefetch_related('payment_set')
        .filter(
            Q(is_trial_period=True, subscribed_at__lte=trial_period_should_have_started_at)
            | Q(is_trial_period=False, subscribed_at__lte=subscription_should_have_started_at)
        )
    )
    server_to_users = group_users_by_server(expiring_users)
    for server, users in server_to_users.items():
        with vpn_server.connected_client(server.url, server.password) as vpn_client:
            for user in users:
                unused_payment = user.payment_set.filter(is_used=False).first()
                if unused_payment is None:
                    if not user.is_subscribed:
                        continue
                    logging.debug(f'Used {user.telegram_id} has unused payment')
                    if user.is_trial_period:
                        text = ('Пробный период использования закончился.'
                                ' Продлите подписку чтобы продолжить пользоваться.'
                                ' Стоимость продления 299 рублей'
                                '\nВажно❗️'
                                f'\nПри оплате в комментарии укажите имя вашего файла <b>{user.telegram_id}</b>')
                    else:
                        text = ('Ваша подписка закончилась.'
                                ' Вы отключены от VPN. '
                                'Стоимость продления 299 рублей'
                                '\nВажно❗️'
                                f'\nПри оплате в комментарии укажите имя вашего файла <b>{user.telegram_id}</b>')
                    with transaction.atomic():
                        vpn_server.disable_user(vpn_client, user.uuid)
                        user.is_subscribed = False
                        user.is_trial_period = False
                        user.save()
                    telegram.send_message(user.telegram_id, text, markup)
                else:
                    logging.debug(f'Used {user.telegram_id} has not unused payment')
                    with transaction.atomic():
                        vpn_server.enable_user(vpn_client, user.uuid)
                        unused_payment.is_used = True
                        user.is_subscribed = True
                        user.is_trial_period = False
                        user.subscribed_at = datetime.datetime.utcnow()
                        unused_payment.save()
                        user.save()
                    expire_at = calculate_expiration_time(user.subscribed_at, is_trial_period=False)
                    text = f'✅ Ваша подписка продлена до {expire_at:%H:%M %d.%m.%Y}'
                    telegram.send_message(user.telegram_id, text)


@shared_task
def expiring_users_notification():
    markup = telegram.get_payment_page_markup()
    now = datetime.datetime.utcnow()
    users = User.objects.filter(is_subscribed=True).values('telegram_id', 'subscribed_at', 'is_trial_period')
    strategies = [
        {
            'start': 60 * 60 * 24 - 25,
            'end': 60 * 60 * 24 + 25,
            'text': 'Ваша подписка заканчивается через 24 часа',
        },
        {
            'start': 60 * 60 - 25,
            'end': 60 * 60 + 25,
            'text': 'Ваша подписка заканчивается через 1 час',
        },
    ]
    for user in users:
        expire_at = calculate_expiration_time(user['subscribed_at'], user['is_trial_period'])
        time_before_expiration = (expire_at - now).total_seconds()
        logging.debug(time_before_expiration)
        for strategy in strategies:
            if strategy['start'] <= time_before_expiration <= strategy['end']:
                text = (strategy['text'] +
                        f'\nВажно❗️\nПри оплате в комментарии укажите имя вашего файла <b>{user["telegram_id"]}</b>')
                telegram.send_message(user['telegram_id'], text, markup)
                break
