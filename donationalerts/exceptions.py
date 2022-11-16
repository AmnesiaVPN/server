from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound


class UserPaymentNotFoundError(NotFound):
    default_detail = _('User payment has not been found')
