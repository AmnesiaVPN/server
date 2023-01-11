from core.exceptions import ApplicationError

__all__ = (
    'VPNServerError',
    'UnauthorizedError',
    'UserDoesNotExistInVPNServerError',
    'NoFreeServersError',
)


class VPNServerError(ApplicationError):
    pass


class UnauthorizedError(VPNServerError):
    pass


class UserDoesNotExistInVPNServerError(VPNServerError):
    pass


class NoFreeServersError(VPNServerError):
    pass
