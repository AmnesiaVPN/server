import datetime
import uuid

from telegram_bot.exceptions import UserNotFoundAPIError
from telegram_bot.models import User
from wireguard.models import Server


def get_or_create_user(telegram_id: int, user_uuid: uuid.UUID, server: Server) -> tuple[User, bool]:
    try:
        return User.objects.get(telegram_id=telegram_id), False
    except User.DoesNotExist:
        return User.objects.create(telegram_id=telegram_id, uuid=user_uuid, server=server), True


def get_user_or_raise_404(telegram_id: int) -> User:
    user = User.objects.filter(telegram_id=telegram_id).first()
    if user is None:
        raise UserNotFoundAPIError
    return user


def calculate_expiration_time(
        subscribed_at: datetime.datetime,
        is_trial_period: bool,
) -> datetime.datetime:
    subscription_days_count = 3 if is_trial_period else 30
    return subscribed_at + datetime.timedelta(days=subscription_days_count)
