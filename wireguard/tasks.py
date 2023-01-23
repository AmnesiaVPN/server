import datetime
import logging

from celery import shared_task
from django.conf import settings

from donationalerts.exceptions import UserHasNoUnusedPaymentError
from donationalerts.selectors import get_oldest_unused_payment
from telegram_bot.selectors import get_user, get_subscription_expired_users_with_payments
from telegram_bot.services.scheduled_tasks import remove_previously_scheduled_tasks, create_new_scheduled_tasks
from telegram_bot.services.telegram import TelegramMessagingService, SubscriptionExpiresInHoursMessage
from telegram_bot.services.users import on_subscription_activated, on_subscription_deactivated


@shared_task
def subscription_control_task():
    telegram_messaging_service = TelegramMessagingService(settings.BOT_TOKEN)
    users = get_subscription_expired_users_with_payments()
    for user in users:
        payment = user.payment_set.first()
        on_subscription_activated(telegram_messaging_service=telegram_messaging_service, user=user, payment=payment)
        on_user_subscription_date_updated.delay(telegram_id=user.telegram_id)
        logging.info(f'User {user.telegram_id} subscription was activated')


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


@shared_task
def on_user_subscription_date_updated(*, telegram_id: int):
    user = get_user(telegram_id=telegram_id)

    task_notify_before_1_hour = notify_before_subscription_expires.apply_async(
        kwargs={'telegram_id': user.telegram_id, 'hours_before_expiration': 1},
        eta=user.subscription_expires_at - datetime.timedelta(hours=1),
        expires=user.subscription_expires_at - datetime.timedelta(hours=1, minutes=-5)
    )
    task_notify_before_24_hours = notify_before_subscription_expires.apply_async(
        kwargs={'telegram_id': user.telegram_id, 'hours_before_expiration': 24},
        eta=user.subscription_expires_at - datetime.timedelta(days=1),
        expires=user.subscription_expires_at - datetime.timedelta(days=1, minutes=-5)
    )
    task_handle_user_subscription = on_subscription_expired.apply_async(
        kwargs={'telegram_id': user.telegram_id},
        eta=user.subscription_expires_at,
    )
