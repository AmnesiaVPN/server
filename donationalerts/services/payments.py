from typing import Iterable

from django.db import transaction
from django.utils import timezone

from donationalerts.models import Payment
from donationalerts.schemas import ValidatedDonationalertsPayment
from telegram_bot.models import User
from wireguard.models import Server
from wireguard.services.vpn_server import VPNServerService


def batch_create_payments(
        *,
        validated_payments: Iterable[ValidatedDonationalertsPayment],
        telegram_id_to_user_id: dict[int, int],
):
    payments = [
        Payment(
            donation_id=validated_payment.id,
            created_at=validated_payment.created_at,
            user_id=telegram_id_to_user_id[validated_payment.telegram_id],
        ) for validated_payment in validated_payments
    ]
    Payment.objects.bulk_create(payments)


@transaction.atomic
def activate_subscription(*, user: User, server: Server, payment: Payment):
    payment.is_used = True
    user.subscribed_at = timezone.now()
    user.is_trial_period = False
    payment.save()
    user.save()
    with VPNServerService(base_url=server.url, password=server.password) as vpn_server:
        vpn_server.login()
        vpn_server.enable_user(user.uuid)


def deactivate_subscription(*, user: User, server: Server):
    user.is_trial_period = False
    user.save()
    with VPNServerService(base_url=server.url, password=server.password) as vpn_server:
        vpn_server.login()
        vpn_server.disable_user(user.uuid)
