from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(repr=False)


class UserSignup(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(repr=False)
