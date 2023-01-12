from typing import Iterable

from donationalerts.models import Payment
from donationalerts.schemas import ValidatedDonationalertsPayment


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
