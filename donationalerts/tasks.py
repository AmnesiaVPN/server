import logging

from celery import shared_task
from django.conf import settings

from donationalerts.selectors import get_all_payment_ids
from donationalerts.services.donationalerts import DonationAlertsAPIService, filter_valid_payments
from donationalerts.services.payments import batch_create_payments
from telegram_bot.exceptions import TelegramAPIError
from telegram_bot.selectors import get_all_user_ids_and_telegram_ids
from telegram_bot.services.telegram import TelegramMessagingService


@shared_task
def sync_payments_in_donationalerts_and_server():
    donationalerts_api = DonationAlertsAPIService(settings.DONATION_ALERTS_ACCESS_TOKEN)
    telegram_messaging_service = TelegramMessagingService(settings.BOT_TOKEN)

    existing_payment_ids = get_all_payment_ids()
    existing_users = get_all_user_ids_and_telegram_ids()

    telegram_id_to_user_id = {user['telegram_id']: user['id'] for user in existing_users}
    existing_telegram_ids = set(telegram_id_to_user_id)

    payments_from_donationalerts = donationalerts_api.get_all_payments()

    validated_payments = filter_valid_payments(
        payments=payments_from_donationalerts,
        existing_telegram_ids=existing_telegram_ids,
        previously_existing_payment_ids=existing_payment_ids,
    )
    batch_create_payments(validated_payments=validated_payments, telegram_id_to_user_id=telegram_id_to_user_id)

    text = '✅ Мы получили вашу оплату. Подписка будет автоматически продлена после окончания действующей'
    for validated_payment in validated_payments:
        try:
            telegram_messaging_service.send_message(chat_id=validated_payment.telegram_id, text=text)
        except TelegramAPIError:
            logging.warning(f'Could not send message')
