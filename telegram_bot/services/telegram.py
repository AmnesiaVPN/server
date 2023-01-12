from typing import Collection

import httpx
from django.conf import settings

from telegram_bot.exceptions import TelegramAPIError

__all__ = (
    'TelegramMessagingService',
    'get_payment_page_markup',
)


class TelegramMessagingService:
    __slots__ = ('__api_base_url',)

    def __init__(self, token: str):
        self.__api_base_url = f'https://api.telegram.org/bot{token}'

    def send_message(self, *, chat_id: int, text: str, reply_markup: Collection[Collection[dict]] | None = None):
        url = f'{self.__api_base_url}/sendMessage'
        request_body = {'chat_id': chat_id, 'text': text, 'parse_mode': 'html'}
        if reply_markup is not None:
            request_body['reply_markup'] = reply_markup
        try:
            response = httpx.post(url, json=request_body)
        except httpx.HTTPError:
            raise TelegramAPIError
        if not response.is_success:
            raise TelegramAPIError


def get_payment_page_markup() -> dict[str, list[list[dict]]]:
    return {'inline_keyboard': [[{'text': 'Продлить подписку', 'url': settings.PAYMENT_PAGE_URL}]]}
