from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=255)

class UserRegisterSchema(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=255)

class UserCompactSchema(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    role: str

class LoginSuccessDataSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserCompactSchema

class LoginResponseSchema(BaseModel):
    success: bool = True
    data: LoginSuccessDataSchema
    meta: dict

class UserResponseDataSchema(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    role: str
    status: str
    created_at: datetime

class UserProfileResponseSchema(BaseModel):
    success: bool = True
    data: UserResponseDataSchema
    meta: dict
