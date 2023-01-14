from promocodes.exceptions import PromocodeNotFoundError
from promocodes.models import Promocode

__all__ = ('get_promocode',)


def get_promocode(*, value: str, include_group: bool = False) -> Promocode:
    promocodes = Promocode.objects.filter(value=value)
    if include_group:
        promocodes = promocodes.select_related('group')
    promocode = promocodes.first()
    if promocode is None:
        raise PromocodeNotFoundError
    return promocode
