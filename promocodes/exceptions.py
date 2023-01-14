from core.exceptions import ApplicationError

__all__ = (
    'PromocodeWasActivatedError',
    'PromocodeWasExpiredError',
    'UserAlreadyActivatedPromocodeError',
    'PromocodeNotFoundError',
)


class UserAlreadyActivatedPromocodeError(ApplicationError):
    pass


class PromocodeWasActivatedError(ApplicationError):
    pass


class PromocodeNotFoundError(ApplicationError):
    pass


class PromocodeWasExpiredError(ApplicationError):
    pass
