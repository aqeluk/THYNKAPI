from datetime import datetime
from tortoise import fields
from tortoise.validators import MinLengthValidator, MaxLengthValidator
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from src.user.schemas import User
from pydantic import BaseModel

class TodoModel(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=50, validators=[MinLengthValidator(1), MaxLengthValidator(50)])
    task = fields.CharField(max_length=500, validators=[MinLengthValidator(1), MaxLengthValidator(500)])
    deadline = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)
    last_modified = fields.DatetimeField(auto_now=True)
    author = fields.ForeignKeyField("models.User", related_name="todos")

    class Meta:
        table_description = "todos"

Todo = pydantic_model_creator(TodoModel, name="Todo", exclude_readonly=True)
TodoResponse = pydantic_model_creator(TodoModel, name="TodoResponse")

