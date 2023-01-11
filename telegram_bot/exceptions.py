from core.exceptions import ApplicationError

__all__ = ('UserAlreadyExistsError', 'UserNotFoundError', 'TelegramAPIError')


class UserAlreadyExistsError(ApplicationError):
    pass


class UserNotFoundError(ApplicationError):
    pass


class TelegramAPIError(ApplicationError):
    pass
