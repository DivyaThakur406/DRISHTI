from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    disaster_type = Column(String)
    location = Column(String)
    severity = Column(String)
    status = Column(String, default="Pending")
    affected_people = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    resource_type = Column(String)
    location = Column(String)
    status = Column(String, default="Available")
    quantity = Column(Integer, default=0)