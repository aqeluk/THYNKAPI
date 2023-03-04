import logging
from fastapi import HTTPException, status


class CsvFileException(HTTPException):
    def __init__(self, error_message: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail="Error while processing the CSV file")
        logging.exception(f"CsvFileException: {error_message}")
