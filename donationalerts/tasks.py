import datetime
import itertools

from celery import shared_task
from django.conf import settings
from django.db import transaction, DatabaseError

from donationalerts.models import Payment
from donationalerts.services import DonationAlertsClient, find_donations_with_specific_message
from telegram_bot import telegram
from telegram_bot.models import User
from telegram_bot.services import calculate_expiration_time
from wireguard.exceptions import VPNServerError
from wireguard.services import vpn_server


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
