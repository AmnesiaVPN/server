import logging
from uuid import UUID

from django.db import IntegrityError

from donationalerts.models import Payment
from donationalerts.services.payments import activate_subscription, deactivate_subscription
from telegram_bot.exceptions import UserAlreadyExistsError, TelegramAPIError
from telegram_bot.models import User
from telegram_bot.services.telegram import (
    TelegramMessagingService,
    SubscriptionActivatedMessage,
    SubscriptionExpiredMessage,
)
from wireguard.exceptions import VPNServerError
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
    try:
        activate_subscription(user=user, payment=payment, server=user.server)
    except VPNServerError:
        logging.error(f'Could not activate user {user.telegram_id} subscription')
    message = SubscriptionActivatedMessage(subscription_expires_at=user.subscription_expires_at)
    try:
        telegram_messaging_service.send_message(chat_id=user.telegram_id, message=message)
    except TelegramAPIError:
        logging.error(f'Could not send subscription activation message to user {user.telegram_id}')


def on_subscription_deactivated(
        *,
        telegram_messaging_service: TelegramMessagingService,
        user: User,
):
    try:
        deactivate_subscription(user=user, server=user.server)
    except VPNServerError:
        logging.error(f'Could not deactivate user {user.telegram_id} subscription')
    message = SubscriptionExpiredMessage(telegram_id=user.telegram_id, is_trial_period=user.is_trial_period)
    try:
        telegram_messaging_service.send_message(chat_id=user.telegram_id, message=message)
    except TelegramAPIError:
        logging.error(f'Could not send subscription deactivation message to user {user.telegram_id}')
