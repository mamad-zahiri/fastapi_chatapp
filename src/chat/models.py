from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import BaseModel, EmailStr, Field, field_serializer

# from src.users.models import User


class PrivateChat(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime
    message: str = ""
    file: str = ""
    sender: EmailStr
    seen: bool = False

    @field_serializer("timestamp")
    def serialize_timestamp(self, timestamp: datetime, _info=None):
        return str(timestamp)

    @field_serializer("id")
    def serialize_id(self, id: UUID, _info=None):
        return str(id)


class GroupChat(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime
    message: str = ""
    file: str = ""
    sender: EmailStr
    # sender: Link["User"]
    seen: bool = False


class Group(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str
    # members: List[Link["User"]]
    members: List[EmailStr]
    created_at: datetime
    chats: List[GroupChat]
