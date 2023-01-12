import json
from typing import Collection

import httpx
from django.conf import settings

from telegram_bot.exceptions import TelegramAPIError


def get_payment_page_markup() -> dict[str, list[list[dict]]]:
    return {'inline_keyboard': [[{'text': 'Продлить подписку', 'url': settings.PAYMENT_PAGE_URL}]]}


def send_message(chat_id: int, text: str, reply_markup: Collection[Collection[dict]] | None = None):
    url = f'{settings.TELEGRAM_API_BASE_URL}/sendMessage'
    body = {'chat_id': chat_id, 'text': text, 'parse_mode': 'html'}
    if reply_markup is not None:
        body['reply_markup'] = reply_markup

    try:
        response = httpx.post(url, json=body)
        if not response.is_success:
            raise TelegramAPIError

        if not response.json()['ok']:
            raise TelegramAPIError
    except (httpx.HTTPError, json.JSONDecodeError):
        raise TelegramAPIError
