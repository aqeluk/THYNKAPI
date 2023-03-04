import logging

from fastapi import HTTPException, status


class WholesaleNotFoundException(HTTPException):
    def __init__(self, error_message: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Wholesaler with this id not found")
        logging.exception(f"WholesaleNotFoundException: {error_message}")
