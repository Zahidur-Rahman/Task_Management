from db.models.task import Task,TaskStatusType
from db.models.user import User
from fastapi import HTTPException
from sqlalchemy.orm import Session 
from schemas.task import TaskCreate,TaskStatuseChange
from schemas.task import TaskResponse  


def create_new_task(task: TaskCreate, db: Session, author_id: int):

    # assignee_id = task.assignee_id if task.assignee_id != 0 else author_id
    new_task = Task(
        task_title=task.task_title,
        slug=task.slug,
        description=task.description,
        is_active=task.is_active,
        assignee_id=author_id,
        author_id=author_id
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)



    db.commit()

    return TaskResponse.model_validate(new_task)



def retreive_task(id:int,db:Session):
    task=db.query(Task).filter(Task.id==id).first()
    return task



def retrieve_tasks_by_user(assignee_id:int,db:Session):
    tasks=db.query(Task).filter(Task.assignee_id==assignee_id).all()
    return tasks

def assign_task_to_user(task_id:int,assignee_id:int,db:Session,restricted_status:str,current_user_id:int):
    task=db.query(Task).filter(
        Task.id==task_id,
        Task.status!=restricted_status,
        (Task.author_id == current_user_id) | (Task.assignee_id == current_user_id)
    ).first()
    if not task:
        return None
    task.assignee_id=assignee_id
    db.commit()
    db.refresh(task)
    return task


def delete_task_by_id(id: int, db: Session, deleting_user_id:int):
    task_in_db = db.query(Task).filter(Task.id == id).first()

    if not task_in_db:
        return {"error": f"Task with id {id} not found"}
    if task_in_db.assignee_id != deleting_user_id:
        return{"error":"Only the assignee can delete this task"}
    db.delete(task_in_db)
    db.commit()
    return {"msg": f"Task with id {id} has been deleted"}

def change_task_status(id: int, new_status: TaskStatusType, db: Session, assignee_id: int):
    task = db.query(Task).filter(Task.id == id, Task.assignee_id == assignee_id).first()
    if not task:
        return None
    task.status = new_status
    db.commit()
    db.refresh(task)
    return task

    
    