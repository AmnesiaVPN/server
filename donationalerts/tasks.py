import datetime
import itertools

from celery import shared_task
from django.conf import settings
from django.db import transaction, DatabaseError

from donationalerts.models import Payment
from donationalerts.services import DonationAlertsClient, find_donations_with_specific_message
from telegram_bot import telegram
from telegram_bot.exceptions import TelegramAPIError
from telegram_bot.models import User
from telegram_bot.services import calculate_expiration_time
from wireguard.exceptions import VPNServerError
from wireguard.services import vpn_server


@shared_task
def sync_payments_in_donationalerts_and_server():
    client = DonationAlertsClient(settings.DONATION_ALERTS_ACCESS_TOKEN)
    donations_from_donationalerts = tuple(itertools.chain.from_iterable(client.iter_all_donations()))
    donation_ids_in_database = set(Payment.objects.values_list('donation_id'))
    donations_not_in_database = [donation for donation in donations_from_donationalerts
                                 if donation.id not in donation_ids_in_database]

    users = User.objects.values('id', 'telegram_id')

    donations_to_insert_to_database = []
    user_telegram_ids_to_be_notified = []
    for donation in donations_not_in_database:
        for user in users:
            if str(user['telegram_id']) not in donation.message.lower():
                continue
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
            print(f'Could not send message to user {telegram_id}')


@shared_task
def check_user_payments():
    client = DonationAlertsClient(settings.DONATION_ALERTS_ACCESS_TOKEN)

    donations = tuple(itertools.chain.from_iterable(client.iter_all_donations()))

    users = User.objects.filter(is_subscribed=False).select_related('server').prefetch_related('payment_set')

    for user in users:
        registered_donation_ids = set(user.payment_set.values_list('donation_id', flat=True))
        user_donations = find_donations_with_specific_message(str(user.telegram_id), donations)
        unregistered_donations = [donation for donation in user_donations if donation.id not in registered_donation_ids]

        if not unregistered_donations:
            continue
        donation = unregistered_donations[0]

        try:
            with transaction.atomic():
                with vpn_server.connected_client(user.server.url, user.server.password) as vpn_client:
                    vpn_server.enable_user(vpn_client, user.uuid)
                Payment.objects.create(user=user, donation_id=donation.id)
                user.subscribed_at = datetime.datetime.utcnow()
                user.is_subscribed = True
                user.save()
        except DatabaseError:
            print('error check payment')
        except VPNServerError:
            print('vpn server error')
        else:
            expire_at = calculate_expiration_time(user.subscribed_at, is_trial_period=False) + datetime.timedelta(hours=3)
            text = f'✅ Ваша подписка продлена до {expire_at:%H:%M %d.%m.%Y}'
            telegram.send_message(user.telegram_id, text)
