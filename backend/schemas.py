from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str
    role: str


class IncidentCreate(BaseModel):
    title: str
    description: str
    disaster_type: str
    location: str
    severity: str
    affected_people: int = 0


class IncidentResponse(IncidentCreate):
    id: int
    status: str

    class Config:
        from_attributes = True


class ResourceCreate(BaseModel):
    name: str
    resource_type: str
    location: str
    quantity: int = 0
    status: str = "Available"


class ResourceResponse(ResourceCreate):
    id: int

    class Config:
        from_attributes = True