from datetime import date

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    email: EmailStr
    date_of_birth: date
    gender: str
    password: str = Field(min_length=8)


class SignupResponse(BaseModel):
    message: str
    user_id: str