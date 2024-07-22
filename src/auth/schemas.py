from pydantic import BaseModel, EmailStr, SecretStr


class UserSignup(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: SecretStr
