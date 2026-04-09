class DomainException(Exception):
    pass


class NotFoundError(DomainException):
    pass


class UserNotFoundError(NotFoundError):
    pass


class BranchNotFoundError(NotFoundError):
    pass


class RoleNotFoundError(NotFoundError):
    pass


class UserInactiveError(DomainException):
    pass


class InvalidCredentialsError(DomainException):
    pass


class EmailAlreadyExistsError(DomainException):
    pass


class BranchAlreadyExistsError(DomainException):
    pass


class InvalidTokenError(DomainException):
    pass


class BusinessRuleViolationError(DomainException):
    pass


class TaxRateNotFoundError(NotFoundError):
    pass


class TaxRateIsDefaultError(DomainException):
    """Raised when trying to deactivate the current default tax rate."""
    pass


class CategoryNotFoundError(NotFoundError):
    pass


class ProductNotFoundError(NotFoundError):
    pass


class ModifierNotFoundError(NotFoundError):
    pass


class ModifierHasHistoryError(DomainException):
    """Raised when trying to delete a modifier that is referenced in order history."""
    pass
