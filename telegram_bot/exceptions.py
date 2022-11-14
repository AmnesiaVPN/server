from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException, status


class UserAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('User is already registered')


class UserNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('User not found')
