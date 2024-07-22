from datetime import datetime

from pydantic import BaseModel, EmailStr, SecretStr


class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    email_verified: bool
    password: SecretStr
    last_seen: datetime
