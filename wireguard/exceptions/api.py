from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException

__all__ = ('NoFreeServersAPIError', 'VPNServerAPIError')


class NoFreeServersAPIError(APIException):
    default_detail = _('No free servers')


class VPNServerAPIError(APIException):
    default_detail = _('VPN server error')
