from telegram_bot.models import User


def get_user_or_raise_404(*, telegram_id: int, include_server: bool = False) -> User:
    users = User.objects.filter(telegram_id=telegram_id)
    if include_server:
        users = users.select_related('server')
    user = users.first()
    if user is None:
        raise
    return user
