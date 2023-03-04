import logging
from fastapi import HTTPException, status


class DetailNotAllowedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="There already is a user by that detail")
        logging.exception("DetailNotAllowedException: There already is a user by that detail")


class VerificationKeyNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Verification key not found")
        logging.exception(f"VerificationKeyNotFoundException: Verification key not found")


class UserVerifiedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="User already verified")
        logging.exception(f"UserVerifiedException: User already verified")


class UserUpdateException(HTTPException):
    def __init__(self, error_message: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="Could not update user details")
        logging.exception(f"UserUpdateException: {error_message}")

