from fastapi import APIRouter, Depends
from tortoise.contrib.fastapi import HTTPNotFoundError
from typing import List
from src.todos.schemas import Todo, TodoResponse
from src.todos.schemas import TodoModel
from src.user.services import get_current_user
from src.exceptions import ServerErrorException, UnauthorizedUserException
from src.todos.exceptions import TodoNotFoundException
from datetime import datetime

router = APIRouter(
    prefix="/todo",
    tags=["Todos"]
)


@router.post("/", response_description="Create Todo", response_model=TodoResponse)
async def create_todo(todo_info: Todo, current_user=Depends(get_current_user)):
    try:
        todo_info_dict = todo_info.dict(exclude_unset=True)
        todo_info_dict["author_name"] = current_user.name
        todo_info_dict["author_id"] = current_user.id
        todo_info_dict["created_at"] = datetime.utcnow()
        todo_info_dict["last_modified"] = datetime.utcnow()

        todo = await TodoModel.create(**todo_info_dict)
        return await TodoResponse.from_tortoise_orm(todo)
    except Exception as e:
        raise ServerErrorException(str(e))


@router.get("/", response_description="Get All Todos", response_model=List[TodoResponse])
async def get_todos(limit: int = 4, orderby: str = "deadline"):
    try:
        todos = await TodoModel.all().order_by(orderby).limit(limit).prefetch_related("author_id")
        return [await TodoResponse.from_tortoise_orm(todo) for todo in todos]
    except Exception as e:
        raise ServerErrorException(str(e))


@router.get("/{todo_id}", response_description="Get Specific Todo", response_model=TodoResponse)
async def get_todo(todo_id: int):
    try:
        todo = await TodoModel.get(id=todo_id)
        return await TodoResponse.from_tortoise_orm(todo)
    except TodoModel.DoesNotExist:
        raise TodoNotFoundException(todo_id=todo_id)
    except Exception as e:
        raise ServerErrorException(str(e))


@router.put("/{todo_id}", response_description="Update Todo", response_model=TodoResponse)
async def update_todo(todo_id: int, todo_info: Todo, current_user=Depends(get_current_user)):
    try:
        todo = await TodoModel.get(id=todo_id)
        if todo.author_id == current_user.id:
            todo_info_dict = todo_info.dict(exclude_unset=True)
            if len(todo_info_dict) >= 1:
                for key, value in todo_info_dict.items():
                    setattr(todo, key, value)
                todo.last_modified = datetime.utcnow()
                await todo.save()
            return await TodoResponse.from_tortoise_orm(todo)
        else:
            raise UnauthorizedUserException()
    except TodoModel.DoesNotExist:
        raise TodoNotFoundException(todo_id=todo_id)
    except Exception as e:
        raise ServerErrorException(str(e))


@router.delete("/{todo_id}", response_description="Delete Todo")
async def delete_todo(todo_id: int, current_user=Depends(get_current_user)):
    try:
        todo = await TodoModel.get(id=todo_id)
        if todo.author_id == current_user.id:
            await todo.delete()
            return {"response": "Successfully deleted todo"}
        else:
            raise UnauthorizedUserException()
    except TodoModel.DoesNotExist:
        raise TodoNotFoundException(todo_id=todo_id)
    except Exception as e:
        raise ServerErrorException(str(e))

