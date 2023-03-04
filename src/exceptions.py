import logging
from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    def __init__(self, error_message: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id not found")
        logging.exception(f"UserNotFoundException: {error_message}")


class ProductNotFoundException(HTTPException):
    def __init__(self, error_message: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Product with this id not found")
        logging.exception(f"ProductNotFoundException: {error_message}")


class InvalidIdException(HTTPException):
    def __init__(self, error_message: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid id provided")
        logging.exception(f"InvalidIdException: {error_message}")


class InvalidFileExtensionException(HTTPException):
    def __init__(self, error_message: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="File extension not allowed")
        logging.exception(f"InvalidFileExtensionException: {error_message}")


class UnauthorizedUserException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated to perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )
        logging.exception("UnauthorizedUserException: Not authenticated to perform this action")


class ServerErrorException(HTTPException):
    def __init__(self, error_message: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
        logging.exception(f"ServerErrorException: {error_message}")
