from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound

__all__ = ('UserAlreadyExistsAPIError', 'UserNotFoundAPIError')


class UserAlreadyExistsAPIError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('User is already registered')


class UserNotFoundAPIError(NotFound):
    default_detail = _('User not found')