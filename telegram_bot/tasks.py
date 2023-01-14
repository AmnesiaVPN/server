import logging
import time

from celery import shared_task
from django.conf import settings

from telegram_bot.exceptions import TelegramAPIError
from telegram_bot.models import User
from telegram_bot.services.telegram import TelegramMessagingService, CustomMessage


@shared_task
def start_broadcasting(text: str, results_notify_to: int | None = None):
    telegram_messaging_service = TelegramMessagingService(settings.BOT_TOKEN)
    user_telegram_ids = User.objects.values_list('telegram_id', flat=True)
    users_count = len(user_telegram_ids)

    message = CustomMessage(text=text)
    sent_messages_count = 0
    for telegram_id in user_telegram_ids:
        try:
            telegram_messaging_service.send_message(chat_id=telegram_id, message=message)
        except TelegramAPIError:
            logging.warning(f'Could not send message')
        else:
            sent_messages_count += 1
        finally:
            time.sleep(0.5)

    if results_notify_to is not None:
        report = f'{sent_messages_count}/{users_count} пользователей получили рассылку'
        message = CustomMessage(text=report)
        telegram_messaging_service.send_message(chat_id=results_notify_to, message=message)
