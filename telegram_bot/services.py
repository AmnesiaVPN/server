from uuid import UUID

from django.db import IntegrityError

from telegram_bot.exceptions import UserAlreadyExistsError
from telegram_bot.models import User
from wireguard.models import Server

__all__ = ('create_user',)


def create_user(*, telegram_id: int, user_uuid: UUID, server: Server) -> User:
    try:
        return User.objects.create(telegram_id=telegram_id, uuid=user_uuid, server=server)
    except IntegrityError:
        raise UserAlreadyExistsError
