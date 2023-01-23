import logging

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from donationalerts.exceptions import UserHasNoUnusedPaymentError
from donationalerts.selectors import get_oldest_unused_payment
from telegram_bot.exceptions import TelegramAPIError
from telegram_bot.models import User
from telegram_bot.selectors import get_user, get_subscribed_users, get_subscription_expired_users_with_payments
from telegram_bot.services.telegram import TelegramMessagingService, SubscriptionExpiresInHoursMessage
from telegram_bot.services.users import on_subscription_activated, on_subscription_deactivated


@shared_task
def subscription_control_task():
    telegram_messaging_service = TelegramMessagingService(settings.BOT_TOKEN)
    users = get_subscription_expired_users_with_payments()
    for user in users:
        payment = user.payment_set.first()
        on_subscription_activated(telegram_messaging_service=telegram_messaging_service, user=user, payment=payment)
        logging.info(f'User {user.telegram_id} subscription was activated')


def check_subscription(telegram_messaging_service: TelegramMessagingService, user: User):
    try:
        payment = get_oldest_unused_payment(user=user)
    except UserHasNoUnusedPaymentError:
        on_subscription_deactivated(telegram_messaging_service=telegram_messaging_service, user=user)
    else:
        on_subscription_activated(telegram_messaging_service=telegram_messaging_service, user=user, payment=payment)


@shared_task
def subscription_expiration_control_task():
    telegram_messaging_service = TelegramMessagingService(settings.BOT_TOKEN)
    now = timezone.now()
    users = get_subscribed_users()
    for user in users:
        seconds_before_expiration = (user.subscription_expires_at - now).total_seconds()
        logging.debug(f'User ID{user.telegram_id} {seconds_before_expiration} seconds before expiration')
        hours_before_expiration = int(seconds_before_expiration // 3600)
        is_last_minute_of_hour = seconds_before_expiration % 3600 <= 60
        if hours_before_expiration == 0 and is_last_minute_of_hour:
            check_subscription(telegram_messaging_service, user)
            continue
        if hours_before_expiration not in (1, 24) or not is_last_minute_of_hour:
            continue
        message = SubscriptionExpiresInHoursMessage(
            telegram_id=user.telegram_id,
            hours_before_expiration=hours_before_expiration,
        )
        try:
            telegram_messaging_service.send_message(chat_id=user.telegram_id, message=message)
        except TelegramAPIError:
            logging.error(f'Could not send message to user {user.telegram_id}')


@shared_task
def on_subscription_expired(telegram_id: int):
    telegram_messaging_service = TelegramMessagingService(settings.BOT_TOKEN)
    user = get_user(telegram_id=telegram_id)
    try:
        get_oldest_unused_payment(user=user)
    except UserHasNoUnusedPaymentError:
        on_subscription_deactivated(telegram_messaging_service=telegram_messaging_service, user=user)


@shared_task
def notify_before_subscription_expires(telegram_id: int, hours_before_expiration: int):
    message = SubscriptionExpiresInHoursMessage(
        telegram_id=telegram_id,
        hours_before_expiration=hours_before_expiration,
    )
    telegram_messaging_service = TelegramMessagingService(settings.BOT_TOKEN)
    telegram_messaging_service.send_message(chat_id=telegram_id, message=message)
