from datetime import datetime
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import AnyUrl, EmailStr, Field, field_serializer


class UuidDocument(Document):
    id: UUID = Field(default_factory=uuid4)

    @field_serializer("id")
    def serialize_id(self, id: UUID, _info=None):
        return str(id)


class PrivateChat(UuidDocument):
    message: str = ""
    file: AnyUrl = ""
    sender: Link["User"]
    receiver: Link["User"]
    timestamp: datetime
    seen: bool = False

    class Settings:
        name = "privatse_chats"

    @field_serializer("timestamp")
    def serialize_timestamp(self, timestamp: datetime, _info=None):
        return str(timestamp)


class GroupChat(UuidDocument):
    message: str = ""
    file: AnyUrl = ""
    sender: Link["User"]
    receiver: Link["Group"]
    timestamp: datetime
    seen: bool = False

    class Settings:
        name = "groups_chats"

    @field_serializer("timestamp")
    def serialize_timestamp(self, timestamp: datetime, _info=None):
        return str(timestamp)


class Group(UuidDocument):
    name: str

    class Settings:
        name = "groups"


class User(UuidDocument):
    first_name: str = ""
    last_name: str = ""
    email: EmailStr
    password: str = Field(repr=False)
    last_seen: datetime

    class Settings:
        name = "users"

    @field_serializer("last_seen")
    def serialize_last_seen(self, last_seen: datetime, _info=None):
        return str(last_seen)
