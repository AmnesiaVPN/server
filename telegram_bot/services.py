import datetime

from rest_framework.generics import get_object_or_404

from telegram_bot.models import User


def get_or_create_user(telegram_id: int) -> tuple[User, bool]:
    return User.objects.get_or_create(telegram_id=telegram_id)


def get_user_by_telegram_id(telegram_id: int) -> User:
    return get_object_or_404(User, telegram_id=telegram_id)


def calculate_expiration_time(
        subscribed_at: datetime.datetime,
        is_trial_period: bool,
) -> datetime.datetime:
    subscription_days_count = 3 if is_trial_period else 30
    return subscribed_at + datetime.timedelta(days=subscription_days_count)
