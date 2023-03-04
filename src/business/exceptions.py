import logging

from fastapi import HTTPException, status


class BusinessNotFoundException(HTTPException):
    def __init__(self, error_message: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Business with this id not found")
        logging.exception(f"BusinessNotFoundException: {error_message}")
