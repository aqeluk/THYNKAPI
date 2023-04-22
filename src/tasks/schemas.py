from typing import Optional
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from tortoise import fields

class Task(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    completed = fields.BooleanField(default=False)
    user_id = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tasks"

Task_Pydantic = pydantic_model_creator(Task, name="Task")
TaskIn_Pydantic = pydantic_model_creator(Task, name="TaskIn", exclude_readonly=True)

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
