import datetime

from django.db import transaction
from django.utils import timezone

from promocodes.exceptions import (
    PromocodeNotFound,
    PromocodeWasExpired,
    PromocodeWasActivated,
    UserAlreadyActivatedPromocode,
)
from promocodes.models import Promocode
from telegram_bot.models import User

__all__ = (
    'activate_subscription_via_promocode',
    'get_promocode_or_raise_404',
    'validate_user_and_promocode',
    'is_promocode_expired',
    'is_promocode_activated',
)


def get_promocode_or_raise_404(value: str) -> Promocode:
    promocode = Promocode.objects.select_related('group').filter(value=value).first()
    if promocode is None:
        raise PromocodeNotFound
    return promocode


def is_promocode_expired(expires_at: datetime.datetime | None) -> bool:
    if expires_at is None:
        return False
    return timezone.now() < expires_at


def is_promocode_activated(promocode: Promocode) -> bool:
    return promocode.activated_by is not None or promocode.activated_at is not None


def validate_user_and_promocode(user: User, promocode: Promocode) -> None:
    """Raise API Exceptions if promocode is not valid for activation.

    Args:
        user: User orm object.
        promocode: Promocode orm object.

    Raises:
        promocodes.exceptions.PromocodeWasExpired if promocode was expired.
        promocodes.exceptions.PromocodeWasActivated if promocde was already activated.
    """
    if user.has_used_promocode:
        raise UserAlreadyActivatedPromocode
    if is_promocode_expired(promocode.group.expire_at):
        raise PromocodeWasExpired
    if is_promocode_activated(promocode):
        raise PromocodeWasActivated


@transaction.atomic
def activate_subscription_via_promocode(user: User, promocode: Promocode) -> User:
    now = timezone.now()
    promocode.activated_at = now
    promocode.activated_by = user
    promocode.save()
    user.subscribed_at = now
    user.is_subscribed = True
    user.is_trial_period = False
    user.has_used_promocode = True
    user.save()
    return user
