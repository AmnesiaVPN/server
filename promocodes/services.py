import string

from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string

from promocodes.exceptions import (
    UserAlreadyActivatedPromocodeError,
    PromocodeWasExpiredError,
    PromocodeWasActivatedError,
)
from promocodes.models import Promocode, PromocodesGroup
from telegram_bot.models import User

__all__ = (
    'activate_subscription_via_promocode',
    'PromocodeValidator',
    'batch_create_promocodes',
)


class PromocodeValidator:

    def __init__(self, *, user: User, promocode: Promocode):
        self.__user = user
        self.__promocode = promocode

    @property
    def is_expired(self) -> bool:
        if self.__promocode.group.expire_at is None:
            return False
        return timezone.now() > self.__promocode.group.expire_at

    @property
    def is_already_activated(self) -> bool:
        return self.__promocode.activated_by is not None or self.__promocode.activated_at is not None

    @property
    def is_user_activated_promocode(self) -> bool:
        return self.__user.has_activated_promocode

    def validate(self):
        if self.is_user_activated_promocode:
            raise UserAlreadyActivatedPromocodeError
        if self.is_expired:
            raise PromocodeWasExpiredError
        if self.is_already_activated:
            raise PromocodeWasActivatedError


@transaction.atomic
def activate_subscription_via_promocode(user: User, promocode: Promocode):
    now = timezone.now()
    promocode.activated_at = now
    promocode.activated_by = user
    promocode.save()
    user.subscribed_at = now
    user.is_trial_period = False
    user.has_activated_promocode = True
    user.save()


def batch_create_promocodes(*, group: PromocodesGroup, count: int):
    allowed_chars = string.ascii_uppercase + string.digits
    promocodes = [Promocode(group=group, value=get_random_string(length=8, allowed_chars=allowed_chars))
                  for _ in range(count)]
    Promocode.objects.bulk_create(promocodes, ignore_conflicts=True)
