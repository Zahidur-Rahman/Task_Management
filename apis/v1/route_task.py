from fastapi import APIRouter, Depends,status,HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.task import TaskCreate, TaskResponse,TaskAssignment,TaskStatuseChange
from db.repository.task import create_new_task,retreive_task,retrieve_tasks_by_user,assign_task_to_user
from db.repository.task import delete_task_by_id,change_task_status
from db.models.user import User
from apis.v1.route_login import get_current_user 


router = APIRouter()

@router.post("/", response_model=TaskResponse,status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    task_obj = create_new_task(task=task, db=db, author_id=current_user.id)
    return TaskResponse.model_validate(task_obj)  # Use model_validate instead of from_orm


@router.get("/{id}",response_model=TaskResponse)
def get_task(id:int,db:Session=Depends(get_db)):
    task=retreive_task(id=id,db=db)
    if not task:
        raise HTTPException(detail=f"Task with id {id} is not found",status_code=status.HTTP_404_NOT_FOUND)
    
    return task


@router.get("/assignee/tasks",response_model=list[TaskResponse])
def get_user_task(assignee:User=Depends(get_current_user), db:Session=Depends(get_db)):
    tasks=retrieve_tasks_by_user(assignee_id=assignee.id,db=db)
    # if not tasks:
    #     raise HTTPException(detail=f"No tasks are assigned to {assignee_id}",status_code=status.HTTP_404_NOT_FOUND)
    return tasks

@router.put("/assign_task", response_model=TaskResponse)
def assign_task(task_assignment: TaskAssignment, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    

    updated_task = assign_task_to_user(
        task_id=task_assignment.task_id,
        assignee_id=task_assignment.assignee_id,
        db=db,
        restricted_status="Completed",
        current_user_id=current_user.id
    )
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or could not be assigned"
        )
    return updated_task


@router.delete("/{task_id}")
def delete_a_task(task_id: int, db: Session = Depends(get_db) ,current_user : User=Depends(get_current_user)):
    message = delete_task_by_id(id=task_id, db=db, deleting_user_id=current_user.id,task_status="Completed")
    if message.get("error"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message.get("error"))
    
    return {"msg": message.get("msg")}

@router.put("/status/{task_id}", response_model=TaskResponse)
def update_a_task_status(task_id:int,status_update:TaskStatuseChange,db:Session=Depends(get_db), assignee_user:User=Depends(get_current_user)):
    task=change_task_status(id=task_id,new_status=status_update.status,db=db,assignee_id=assignee_user.id)

    if not task:
            raise HTTPException( 
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=f"Task with id {task_id} not found or this task is assigned with another one"
             )
    return task

