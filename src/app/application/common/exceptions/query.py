from app.application.common.exceptions.base import ApplicationError


class PaginationError(ApplicationError):
    pass


class SortingError(ApplicationError):
    pass
