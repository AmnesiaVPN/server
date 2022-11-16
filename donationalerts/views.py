from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from donationalerts.services import DonationAlertsClient, find_user_donation


@api_view(['GET'])
def payment_confirm_view(request, telegram_id: int):
    client = DonationAlertsClient(settings.DONATION_ALERTS_ACCESS_TOKEN)
    donation = find_user_donation(str(telegram_id), client)
    return Response(donation.dict())
