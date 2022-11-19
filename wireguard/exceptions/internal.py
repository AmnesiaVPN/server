__all__ = ('VPNServerError', 'UnauthorizedError')


class VPNServerError(Exception):
    pass


class UnauthorizedError(VPNServerError):
    pass
