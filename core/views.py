from rest_framework.views import exception_handler as default_exception_handler
from rest_framework import exceptions as drf_api_exceptions

from wireguard.exceptions import UserDoesNotExistInVPNServerError


def exception_handler(exc, context):
    """
    HackSoft style guide https://github.com/HackSoftware/Django-Styleguide#errors--exception-handling.
    {
        "message": "Error message",
        "extra": {}
    }
    """
    match exc:
        case UserDoesNotExistInVPNServerError():
            exc = drf_api_exceptions.NotFound('User is not synced-up with VPN server')
    response = default_exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(exc.detail, (list, dict)):
        response.data = {'detail': response.data}
    if isinstance(exc, drf_api_exceptions.ValidationError):
        response.data['message'] = 'Validation error'
        response.data["extra"] = {"fields": response.data["detail"]}
    else:
        response.data['message'] = response.data['detail']
        response.data['extra'] = {}
    del response.data['detail']

    return response
