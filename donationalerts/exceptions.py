from core.exceptions import ApplicationError


class DonationalertsError(ApplicationError):
    pass


class UserHasNoUnusedPaymentError(ApplicationError):
    pass
