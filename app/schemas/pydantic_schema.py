from pydantic import BaseModel
from typing import Optional

class ScanBase(BaseModel):
    scan_name: str
    description: Optional[str] = None
    target: str
    status: str

class ScanCreate(ScanBase):
    pass

class Scan(ScanBase):
    id: int

    class Config:
        orm_mode = True

class User(BaseModel):
    username: str
    email: str
    password: str
    
    class Config:
        orm_mode = True
        model_config = {"from_attributes": True}
    

class UserCreate(User):
    pass


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True
        model_config = {"from_attributes": True}


