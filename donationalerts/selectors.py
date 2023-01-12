from donationalerts.models import Payment

__all__ = ('get_all_payment_ids',)


def get_all_payment_ids() -> set[int]:
    return set(Payment.objects.values_list('donation_id', flat=True))
