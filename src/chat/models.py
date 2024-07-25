from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import BaseModel, Field

# from src.users.models import User


class PrivateChat(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime
    message: str = ""
    file: str = ""
    sender: Link["User"]
    seen: bool = False


class GroupChat(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime
    message: str = ""
    file: str = ""
    sender: Link["User"]
    seen: bool = False


class Group(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str
    members: List[Link["User"]]
    created_at: datetime
    chats: List[GroupChat]
