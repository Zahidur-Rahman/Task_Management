from typing import List,Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from db.models.task import TaskStatusType
from db.models.user import User
class TaskCreate(BaseModel):
    task_title: str
    description: str
    is_active: bool = True
    slug: Optional[str] = None  # Slug field is optional
    # assignee_id:Optional[int]=User.id

    # Validator for generating slug if not provided
    @field_validator('slug', mode='before')
    def generate_slug(cls, value, values):
        if not value and 'task_title' in values:
            return values['task_title'].replace(" ", "-").lower()
        return value
    
    class Config:
        from_attributes = True

class TaskResponse(BaseModel):
    id: int
    task_title: str
    description: str
    slug: str
    is_active: bool
    assigned_at: datetime
    status:TaskStatusType
    assignee_id:int

    class Config:
        from_attributes = True


class TaskAssignment(BaseModel):
    task_id: int
    assignee_id: int

    class Config:
        from_attributes=True


class TaskStatuseChange(BaseModel):
    status:TaskStatusType
    class Config:
        from_attributes=True
