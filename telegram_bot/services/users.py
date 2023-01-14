from uuid import UUID

from django.db import IntegrityError

from donationalerts.models import Payment
from donationalerts.services.payments import activate_subscription, deactivate_subscription
from telegram_bot.exceptions import UserAlreadyExistsError
from telegram_bot.models import User
from telegram_bot.services.telegram import (
    TelegramMessagingService,
    SubscriptionActivatedMessage,
    SubscriptionExpiredMessage,
)
from wireguard.models import Server

__all__ = (
    'create_user',
    'on_subscription_activated',
    'on_subscription_deactivated',
)


def create_user(*, telegram_id: int, user_uuid: UUID, server: Server) -> User:
    try:
        return User.objects.create(telegram_id=telegram_id, uuid=user_uuid, server=server)
    except IntegrityError:
        raise UserAlreadyExistsError


def on_subscription_activated(
        *,
        telegram_messaging_service: TelegramMessagingService,
        user: User,
        payment: Payment,
):
    activate_subscription(user=user, payment=payment, server=user.server)
    message = SubscriptionActivatedMessage(subscription_expires_at=user.subscription_expires_at)
    telegram_messaging_service.send_message(chat_id=user.telegram_id, message=message)


def on_subscription_deactivated(
        *,
        telegram_messaging_service: TelegramMessagingService,
        user: User,
):
    deactivate_subscription(user=user, server=user.server)
    message = SubscriptionExpiredMessage(telegram_id=user.telegram_id, is_trial_period=user.is_trial_period)
    telegram_messaging_service.send_message(chat_id=user.telegram_id, message=message)
