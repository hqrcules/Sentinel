from pydantic import BaseModel
from typing import Optional


class ServerBase(BaseModel):
    name: str
    job_name: str
    instance: str
    is_active: bool = True


class ServerCreate(ServerBase):
    pass


class ServerUpdate(BaseModel):
    name: Optional[str] = None
    job_name: Optional[str] = None
    instance: Optional[str] = None
    is_active: Optional[bool] = None


class ServerResponse(ServerBase):
    id: int

    class Config:
        from_attributes = True
