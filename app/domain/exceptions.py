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


class RestaurantTableNotFoundError(NotFoundError):
    pass


class OrderNotFoundError(NotFoundError):
    pass


class OrderItemNotFoundError(NotFoundError):
    pass


class OrderAlreadyClosedError(DomainException):
    """Raised when trying to modify a PAID or CANCELLED order."""
    pass


class TableAlreadyOccupiedError(DomainException):
    """Raised when trying to assign a table that already has an open order."""
    pass


class InsufficientPermissionsError(DomainException):
    """Raised when the actor's role is not allowed to perform the action."""
    pass


class DefaultTaxRateNotFoundError(DomainException):
    """Raised when no default tax rate is configured and a product has no explicit rate."""
    pass


class ReservationNotFoundError(NotFoundError):
    pass


class ReservationTerminalStateError(DomainException):
    """Raised when trying to transition a reservation from a terminal state."""
    pass


class ReservationOverlapError(DomainException):
    """Raised when a new/updated reservation would overlap an existing CONFIRMED one."""
    pass


class SystemConfigNotFoundError(NotFoundError):
    pass
