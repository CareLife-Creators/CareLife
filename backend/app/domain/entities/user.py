from datetime import date

from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    email: str
    date_of_birth: date
    gender: str
    password_hash: str