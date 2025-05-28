from pydantic import BaseModel, Field
from app.schemas.personal import PersonalResponse
from typing import Optional


class UserLogin(BaseModel):
    username: str = Field(..., example="johndoe")
    password: str = Field(..., min_length=6, example="secretpassword")


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: PersonalResponse
