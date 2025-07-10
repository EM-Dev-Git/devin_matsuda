from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    user_id: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
