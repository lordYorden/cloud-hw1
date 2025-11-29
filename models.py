from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, ARRAY, String
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import field_serializer, model_serializer
from enum import Enum

ZONE = ZoneInfo('Asia/Jerusalem')

class Criteria(Enum):
    ROLE = "byRole"
    EMAIL_DOMAIN = "byEmailDomain"
    REGISTERATION_TODAY = "byRegistrationToday"

class User(SQLModel, table=True):
    email: str = Field(default=None, primary_key=True)
    name: str
    password: str
    # with timezone info
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
    
    #serialized user the same as example
    @model_serializer(mode='wrap')
    def serialize_model(self, handler):
        data = handler(self)
        return {
            'email': data.get('email'),
            'name': data.get('name'),
            'registrationTimestamp': data.get('registrationTimestamp'),
            'roles': data.get('roles'),
        }
    
class Config:
    arbitrary_types_allowed = True