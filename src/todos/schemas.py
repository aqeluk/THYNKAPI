from datetime import datetime
from tortoise.fields import CharField, DatetimeField, IntField
from tortoise.validators import MinLengthValidator, MaxLengthValidator
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from pydantic import BaseModel

class TodoModel(Model):
    id = IntField(pk=True)
    title = CharField(max_length=50, validators=[MinLengthValidator(1), MaxLengthValidator(50)])
    task = CharField(max_length=500, validators=[MinLengthValidator(1), MaxLengthValidator(500)])
    deadline = DatetimeField()
    author_name = CharField(max_length=50, validators=[MinLengthValidator(1), MaxLengthValidator(50)])
    author_id = CharField(max_length=50, validators=[MinLengthValidator(1), MaxLengthValidator(50)])
    created_at = DatetimeField(auto_now_add=True)
    last_modified = DatetimeField(auto_now=True)

    class Meta:
        table_description = "todos"

Todo = pydantic_model_creator(TodoModel, name="Todo", exclude_readonly=True)
TodoResponse = pydantic_model_creator(TodoModel, name="TodoResponse")
