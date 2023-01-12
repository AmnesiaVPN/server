from typing import TypedDict

__all__ = ('UserIDAndTelegramID',)


class UserIDAndTelegramID(TypedDict):
    id: int
    telegram_id: int
