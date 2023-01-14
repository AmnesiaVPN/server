from django.db.models import QuerySet

from telegram_bot.exceptions import UserNotFoundError
from telegram_bot.models import User, ScheduledTask
from telegram_bot.schemas import UserIDAndTelegramID

__all__ = (
    'get_user',
    'get_all_user_ids_and_telegram_ids',
    'get_previously_scheduled_tasks',
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
