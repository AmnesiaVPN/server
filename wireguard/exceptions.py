class VPNServerError(Exception):
    pass


class UnauthorizedError(VPNServerError):
    pass


class NotFoundInCollectionError(Exception):
    pass
