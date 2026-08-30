from typing import Optional
from pydantic import BaseModel, EmailStr

class PasswordReset(BaseModel):
    email: EmailStr
    token: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class EmailVerification(BaseModel):
    email: EmailStr
    token: str

class EmailVerificationRequest(BaseModel):
    email: EmailStr

class ChangePassword(BaseModel):
    current_password: str
    new_password: str 