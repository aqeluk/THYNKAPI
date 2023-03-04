from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from typing import List
from .schemas import Todo, TodoResponse
from database import db
from user.services import get_current_user
from exceptions import ServerErrorException, UnauthorizedUserException
from .exceptions import TodoNotFoundException


router = APIRouter(
    prefix="/todo",
    tags=["Todos"]
)


@router.post("/", response_description="Create Todo", response_model=TodoResponse)
async def create_todo(todo_info: Todo, current_user=Depends(get_current_user)):
    try:
        todo_info = jsonable_encoder(todo_info)
        todo_info["author_name"] = current_user["name"]
        todo_info["author_id"] = current_user["_id"]
        todo_info["created_at"] = datetime.utcnow()
        todo_info["last_modified"] = datetime.utcnow()
        new_todo = await db["todo"].insert_one(todo_info)
        created_todo = await db["todo"].find_one({"_id": new_todo.inserted_id})
        return created_todo
    except Exception as e:
        raise ServerErrorException(str(e))


@router.get("/", response_description="Get All Todos", response_model=List[TodoResponse])
async def get_todos(limit: int = 4, orderby: str = "deadline"):
    try:
        todos = await db["todo"].find({"$query": {}, "$orderby": {orderby: -1}}).to_list(limit)
        return todos
    except Exception as e:
        raise ServerErrorException(str(e))


@router.get("/{todo_id}", response_description="Get Specific Todo", response_model=TodoResponse)
async def get_todo(todo_id: str):
    try:
        blog_post = await db["todo"].find_one({"_id": todo_id})
        return blog_post
    except Exception as e:
        raise ServerErrorException(str(e))


@router.put("/{todo_id}", response_description="Update Todo", response_model=TodoResponse)
async def update_todo(todo_id: str, todo_info: Todo, current_user=Depends(get_current_user)):
    if todo := await db["todo"].find_one({"_id": todo_id}):
        if todo["author_id"] == current_user["_id"]:
            try:
                todo_info = {k: v for k, v in todo_info.dict().items() if v is not None}
                if len(todo_info) >= 1:
                    selected_todo = await db["todo"].update_one({"_id": todo_id}, {"$set": todo_info})
                    if selected_todo.modified_count == 1:
                        if (updated_blog := await db["todo"].find_one({"_id": todo_id})) is not None:
                            return updated_blog
                if (existing_todo := await db["todo"].find_one({"_id": todo_id})) is not None:
                    return existing_todo
                raise TodoNotFoundException(todo_id=todo_id)
            except Exception as e:
                raise ServerErrorException(str(e))
        else:
            raise UnauthorizedUserException()


@router.delete("/{todo_id}", response_description="Delete Todo")
async def delete_todo(todo_id: str, current_user=Depends(get_current_user)):
    if todo := await db["todo"].find_one({"_id": todo_id}):
        if todo["author_id"] == current_user["_id"]:
            try:
                deleted_todo = await db["todo"].delete_one({"_id": todo_id})
                if deleted_todo.deleted_count == 1:
                    return {"response": "Successfully deleted todo"}
                raise TodoNotFoundException(todo_id=todo_id)
            except Exception as e:
                raise ServerErrorException(str(e))
        else:
            raise UnauthorizedUserException()
        