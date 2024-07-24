from datetime import datetime
from uuid import UUID, uuid4

from beanie import Document
from pydantic import EmailStr, Field


class User(Document):
    id: UUID = Field(default_factory=uuid4)
    first_name: str = ""
    last_name: str = ""
    email: EmailStr
    email_verified: bool
    password: str = Field(repr=False)
    last_seen: datetime

    class Settings:
        name = "users"
