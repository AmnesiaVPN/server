from donationalerts.exceptions import UserHasNoUnusedPaymentError
from donationalerts.models import Payment

from telegram_bot.models import User

__all__ = ('get_all_payment_ids', 'get_oldest_unused_payment')


def get_all_payment_ids() -> set[int]:
    return set(Payment.objects.values_list('donation_id', flat=True))


def get_oldest_unused_payment(*, user: User | int) -> Payment:
    payment = Payment.objects.filter(is_used=False, user_id=user).order_by('-created_at').first()
    if payment is None:
        raise UserHasNoUnusedPaymentError
    return payment
