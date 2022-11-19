import datetime
import itertools

from django.conf import settings
from django.db import transaction, DatabaseError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from donationalerts.exceptions import UserPaymentNotFoundError
from donationalerts.models import Payment
from donationalerts.services import DonationAlertsClient, find_donations_with_specific_message
from telegram_bot.exceptions import UserNotFoundError
from telegram_bot.models import User


@api_view(['GET'])
def payment_confirm_view(request, telegram_id: int):
    client = DonationAlertsClient(settings.DONATION_ALERTS_ACCESS_TOKEN)
    donations = itertools.chain.from_iterable(client.iter_all_donations())
    user_donations = find_donations_with_specific_message(str(telegram_id), donations)

    user = User.objects.filter(telegram_id=telegram_id).select_related('server').first()
    registered_donation_ids = set(Payment.objects.filter(user=user).values_list('donation_id', flat=True))
    if user is None:
        raise UserNotFoundError

    try:
        user_donation = [user_donation for user_donation in user_donations
                         if user_donation.id not in registered_donation_ids][0]
    except IndexError:
        raise UserPaymentNotFoundError

    try:
        with transaction.atomic():
            Payment.objects.create(user=user, donation_id=user_donation.id)
            user.subscribed_at = datetime.datetime.utcnow()
            user.is_subscribed = True
    except DatabaseError:
        raise APIException

    return Response(status=status.HTTP_200_OK)
