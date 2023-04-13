from datetime import datetime
from src.models import PyObjectId
from bson import ObjectId
from pydantic import BaseModel, Field

class Todo(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(..., min_length=1, max_length=50)
    task: str = Field(..., min_length=1, max_length=500)
    deadline: datetime = Field(...)

    def validate_deadline(v):
        return v > datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) if v else False

    @classmethod
    def validate_dict(cls, values):
        if 'deadline' in values:
            if not cls.validate_deadline(values['deadline']):
                raise ValueError("deadline must be after the current month and year")
        return values

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "todo title",
                "task": "task content",
                "deadline": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }


class TodoResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(..., min_length=1, max_length=50)
    task: str = Field(..., min_length=1, max_length=500)
    deadline: datetime = Field(...)
    author_name: str = Field(..., min_length=1, max_length=50)
    author_id: str = Field(..., min_length=1, max_length=50)
    created_at: datetime = Field(...)
    last_modified: datetime = Field(...)

    def validate_deadline(v):
        return v > datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) if v else False

    @classmethod
    def validate_dict(cls, values):
        if 'deadline' in values:
            if not cls.validate_deadline(values['deadline']):
                raise ValueError("deadline must be after the current month and year")
        if 'last_modified' in values:
            if not cls.validate_last_modified(values['last_modified']):
                raise ValueError("last_modified must be after the current month and year")
        return values

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "todo title",
                "task": "task content",
                "deadline": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "author_name": "name of the author",
                "author_id": "ID of the author",
                "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "last_modified": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
