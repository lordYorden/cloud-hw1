from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, ARRAY, String
from typing import Optional
from datetime import datetime
from pydantic import field_serializer, model_serializer
from app.models.consts import ZONE


class User(SQLModel, table=True):
    """Database model for User"""
    email: str = Field(default=None, primary_key=True)
    name: str
    password: str
    registrationTimestamp: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(ZONE),
        sa_column=Column(DateTime(timezone=True))
    )
    roles: list[str] = Field(sa_column=Column(ARRAY(String)))
    
    @field_serializer('registrationTimestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        if value:
            return value.astimezone(ZONE).isoformat(timespec='milliseconds')
        return None
    
    @model_serializer(mode='wrap')
    def serialize_model(self, handler):
        data = handler(self)
        return {
            'email': data.get('email'),
            'name': data.get('name'),
            'password': data.get('password'),
            'registrationTimestamp': data.get('registrationTimestamp'),
            'roles': data.get('roles'),
        }

    class Config:
        arbitrary_types_allowed = True
