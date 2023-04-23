from typing import List
from fastapi import APIRouter, Depends
from src.tasks.schemas import Task, Task_Pydantic, TaskIn_Pydantic, TaskUpdate
from src.user.services import get_current_user
from src.exceptions import InvalidIdException, ServerErrorException

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_description="Create a Task", response_model=Task_Pydantic)
async def create_task(task: TaskIn_Pydantic, current_user=Depends(get_current_user)):
    task_data = task.dict()
    task_data["user_id"] = current_user.id
    new_task = await Task.create(**task_data)
    created_task = await Task_Pydantic.from_tortoise_orm(new_task)
    return created_task

@router.get("/", response_description="Get all tasks for the user", response_model=List[Task_Pydantic])
async def get_tasks(current_user=Depends(get_current_user)):
    tasks = await Task_Pydantic.from_queryset(Task.filter(user_id=current_user.id))
    return tasks

@router.put("/{task_id}", response_description="Update Task")
async def update_task(task_id: int, task: TaskUpdate, current_user=Depends(get_current_user)):
    task_obj = await Task.get_or_none(id=task_id, user_id=current_user.id)
    if task_obj:
        task_data = task.dict(exclude_unset=True)
        for key, value in task_data.items():
            setattr(task_obj, key, value)
        await task_obj.save()
        return {"message": "Task updated successfully"}
    else:
        raise ServerErrorException("Task update failed")


@router.delete("/{task_id}", response_description="Delete Task")
async def delete_task(task_id: int, current_user=Depends(get_current_user)):
    deleted_task = await Task.filter(id=task_id, user_id=current_user.id).delete()
    if deleted_task:
        return {"message": "Task deleted successfully"}
    else:
        raise ServerErrorException("Task deletion failed")
