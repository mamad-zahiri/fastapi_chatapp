from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: str = None
    first_name: str
    last_name: str
    email: EmailStr
    email_verified: bool
    password: str = Field(repr=False)
    last_seen: datetime
