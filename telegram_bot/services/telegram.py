import datetime

import httpx
from django.conf import settings

from telegram_bot.exceptions import TelegramAPIError

__all__ = (
    'TelegramMessagingService',
    'SubscriptionExpiredMessage',
    'SubscriptionExpiresInHoursMessage',
    'SubscriptionActivatedMessage',
    'PaymentReceivedMessage',
    'CustomMessage',
)

PAYMENT_PAGE_MARKUP = {
    'inline_keyboard': [
        [
            {
                'text': 'Продлить подписку',
                'url': settings.PAYMENT_PAGE_URL,
            },
        ],
    ],
}


class TelegramMessage:
    text: str | None = None
    reply_markup: dict | None = None

    def get_text(self) -> str:
        return self.text

    def get_reply_markup(self) -> dict:
        return self.reply_markup


class CustomMessage(TelegramMessage):

    def __init__(self, *, text: str):
        self.text = text


class SubscriptionExpiredMessage(TelegramMessage):
    reply_markup = PAYMENT_PAGE_MARKUP

    def __init__(self, *, telegram_id: int, is_trial_period: bool):
        self.__telegram_id = telegram_id
        self.__is_trial_period = is_trial_period

    def get_text(self) -> str:
        first_line = 'Пробный период использования закончился' if self.__is_trial_period else 'Ваша подписка закончилась'
        return (
            f'{first_line}. Вы отключены от VPN. Стоимость продления 299 рублей'
            '\nВажно❗️'
            f'\nПри оплате в комментарии укажите имя вашего файла <b>{self.__telegram_id}</b>'
        )


class SubscriptionExpiresInHoursMessage(TelegramMessage):

    def __init__(self, *, telegram_id: int, hours_before_expiration: int):
        self.__telegram_id = telegram_id
        self.__hours_before_expiration = hours_before_expiration

    def get_text(self) -> str:
        return (
            f'Ваша подписка заканчивается через {self.__hours_before_expiration} час(ов)'
            f'\nВажно❗️\nПри оплате в комментарии укажите имя вашего файла <b>{self.__telegram_id}</b>'
        )


class PaymentReceivedMessage(TelegramMessage):
    text = '✅ Мы получили вашу оплату. Подписка будет автоматически продлена после окончания действующей'


class SubscriptionActivatedMessage(TelegramMessage):

    def __init__(self, *, subscription_expires_at: datetime.datetime):
        self.__subscription_expires_at = subscription_expires_at

    def get_text(self) -> str:
        subscription_expires_at = self.__subscription_expires_at + datetime.timedelta(hours=3)
        return f'✅ Ваша подписка продлена до {subscription_expires_at:%H:%M %d.%m.%Y}'


class TelegramMessagingService:
    __slots__ = ('__api_base_url',)

    def __init__(self, token: str):
        self.__api_base_url = f'https://api.telegram.org/bot{token}'

    def send_message(self, *, chat_id: int, message: TelegramMessage):
        url = f'{self.__api_base_url}/sendMessage'
        request_body = {'chat_id': chat_id, 'text': message.get_text(), 'parse_mode': 'html'}
        reply_markup = message.get_reply_markup()
        if reply_markup is not None:
            request_body['reply_markup'] = reply_markup
        try:
            response = httpx.post(url, json=request_body)
        except httpx.HTTPError:
            raise TelegramAPIError
        if not response.is_success:
            raise TelegramAPIError
