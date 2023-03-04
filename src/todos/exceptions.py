import logging
from fastapi import HTTPException, status


class TodoNotFoundException(HTTPException):
    def __init__(self, todo_id: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog {blog_id} not found")
        logging.exception(f"TodoNotFoundException: Blog {todo_id} not found")
