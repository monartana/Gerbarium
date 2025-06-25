from functools import wraps
from http import HTTPStatus
from logging import getLogger
from fastapi import HTTPException
from common.schema import ApiResponse

logger = getLogger(__name__)


def with_api_exception_handling(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (HTTPException, Exception) as e:
            logger.exception(e)

            if isinstance(e, HTTPException):
                return ApiResponse(status=e.status_code, error=e.detail)

            return ApiResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR, error="Internal Server Error")

    return wrapper


def with_error_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise e

    return wrapper
