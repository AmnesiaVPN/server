import time

from celery import shared_task

from telegram_bot import telegram
from telegram_bot.models import User


@shared_task
def start_broadcasting(text: str, results_notify_to: int | None = None):
    user_telegram_ids = User.objects.values_list('telegram_id', flat=True)
    users_count = len(user_telegram_ids)

    sent_messages_count = 0
    for user_telegram_id in user_telegram_ids:
        is_sent = telegram.send_message(user_telegram_id, text)
        if is_sent:
            sent_messages_count += 1
        time.sleep(0.5)

    if results_notify_to is not None:
        report = f'{sent_messages_count}/{users_count} пользователей получили рассылку'
        telegram.send_message(results_notify_to, report)