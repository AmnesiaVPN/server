import datetime

from django.conf import settings
from django.db.models import QuerySet, F, Q
from django.db.models.functions import Now

from telegram_bot.exceptions import UserNotFoundError
from telegram_bot.models import User, ScheduledTask
from telegram_bot.schemas import UserIDAndTelegramID

__all__ = (
    'get_user',
    'get_all_user_ids_and_telegram_ids',
    'get_subscription_expired_users',
    'get_subscription_expired_users_with_payments',
)


def get_user(*, telegram_id: int, include_server: bool = False) -> User:
    users = User.objects.filter(telegram_id=telegram_id)
    if include_server:
        users = users.select_related('server')
    user = users.first()
    if user is None:
        raise UserNotFoundError
    return user


def get_all_user_ids_and_telegram_ids() -> QuerySet[UserIDAndTelegramID]:
    return User.objects.values('id', 'telegram_id')


def get_previously_scheduled_tasks(*, user: User | int) -> QuerySet[ScheduledTask]:
    return ScheduledTask.objects.filter(user=user)


def get_subscription_expired_users() -> QuerySet[User]:
    return (
        User.objects
        .select_related('server')
        .annotate(
            user_subscription_expires_at=F('subscribed_at') + datetime.timedelta(days=settings.SUBSCRIPTION_DAYS),
            user_trial_period_expires_at=F('subscribed_at') + datetime.timedelta(days=settings.TRIAL_PERIOD_DAYS),
        )
        .filter(
            Q(user_subscription_expires_at__lte=Now(), is_trial_period=False)
            | Q(user_trial_period_expires_at__lte=Now(), is_trial_period=True)
        )
    )


def get_subscription_expired_users_with_payments() -> QuerySet[User]:
    users = get_subscription_expired_users()
    return users.filter(payment__is_used=False).prefetch_related('payment_set')
