import itertools
import logging

from celery import shared_task
from django.conf import settings

from donationalerts.models import Payment
from donationalerts.services import DonationAlertsClient
from telegram_bot import telegram
from telegram_bot.exceptions import TelegramAPIError
from telegram_bot.models import User


@shared_task
def sync_payments_in_donationalerts_and_server():
    client = DonationAlertsClient(settings.DONATION_ALERTS_ACCESS_TOKEN)
    donations_from_donationalerts = tuple(itertools.chain.from_iterable(client.iter_all_donations()))
    donation_ids_in_database = set(Payment.objects.values_list('donation_id', flat=True))
    donations_not_in_database = [donation for donation in donations_from_donationalerts
                                 if donation.id not in donation_ids_in_database]

    logging.debug(f'Donation IDs in database {donation_ids_in_database}')
    users = User.objects.values('id', 'telegram_id')

    donations_to_insert_to_database = []
    user_telegram_ids_to_be_notified = []
    for donation in donations_not_in_database:
        for user in users:
            if str(user['telegram_id']) not in donation.message.lower():
                continue
            logging.info(f'New payment to user {user["telegram_id"]}')
            payment = Payment(user_id=user['id'], created_at=donation.created_at, donation_id=donation.id)
            donations_to_insert_to_database.append(payment)
            user_telegram_ids_to_be_notified.append(user['telegram_id'])

    if donations_to_insert_to_database:
        Payment.objects.bulk_create(donations_to_insert_to_database)

    text = '✅ Мы получили вашу оплату. Подписка будет автоматически продлена после окончания действующей'
    for telegram_id in user_telegram_ids_to_be_notified:
        try:
            telegram.send_message(telegram_id, text)
        except TelegramAPIError:
            logging.warning(f'Could not send message to user {telegram_id}')
