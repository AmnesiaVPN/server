from telegram_bot.exceptions import UserNotFoundError
from telegram_bot.models import User

__all__ = ('get_user',)


def get_user(*, telegram_id: int, include_server: bool = False) -> User:
    users = User.objects.filter(telegram_id=telegram_id)
    if include_server:
        users = users.select_related('server')
    user = users.first()
    if user is None:
        raise UserNotFoundError
    return user
