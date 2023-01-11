from core.exceptions import ApplicationError


class VPNServerError(ApplicationError):
    pass


class UnauthorizedError(VPNServerError):
    pass


class UserDoesNotExistInVPNServerError(VPNServerError):
    pass


class NoFreeServersAPIError(ApplicationError):
    pass
