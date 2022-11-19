import json

import httpx
from django.conf import settings

from telegram_bot.exceptions import TelegramAPIError


def send_message(chat_id: int, text: str) -> bool:
    url = f'{settings.TELEGRAM_API_BASE_URL}/sendMessage'
    try:
        response = httpx.post(url, json={'chat_id': chat_id, 'text': text, 'parse_mode': 'html'})
        return response.json()['ok']
    except (httpx.HTTPError, json.JSONDecodeError):
        raise TelegramAPIError


def send_warning_message(chat_id: int, text: str) -> bool:
    url = f'{settings.TELEGRAM_API_BASE_URL}/sendMessage'
    body = {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': {
            'inline_keyboard': [
                [
                    {'text': 'Продлить подписку', 'url': 'https://www.donationalerts.com/r/blackwebsites'}
                ]
            ]
        }
    }
    try:
        response = httpx.post(url, json=body)
        return response.json()['ok']
    except (httpx.HTTPError, json.JSONDecodeError):
        raise TelegramAPIError
