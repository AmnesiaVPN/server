from rest_framework import status
from rest_framework.exceptions import APIException, NotFound


class UserAlreadyActivatedPromocode(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Each user can activate only one promocode'


class PromocodeWasActivated(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Promocode was already activated'


class PromocodeNotFound(NotFound):
    default_detail = 'Promocode is not found'


class PromocodeWasExpired(APIException):
    status_code = status.HTTP_410_GONE
    default_detail = 'Promocode was already expired'
