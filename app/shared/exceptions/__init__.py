"""Domain and application exceptions."""


class AppError(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str = "APP_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, resource: str, identifier: str | int) -> None:
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            code="NOT_FOUND",
        )
        self.resource = resource
        self.identifier = identifier


class ValidationError(AppError):
    """Input validation failed."""

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message=message, code="VALIDATION_ERROR")
        self.field = field


class RateLimitExceededError(AppError):
    def __init__(self, retry_after: int) -> None:
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after} seconds.",
            code="RATE_LIMIT_EXCEEDED",
        )
        self.retry_after = retry_after


class RecommendationError(AppError):
    """Recommendation engine error."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="RECOMMENDATION_ERROR")
