from datetime import datetime

from pydantic import BaseModel, EmailStr


class AuthUserSchema(BaseModel):
    id: int
    email: EmailStr
    nombre: str
    fecha_registro: datetime
    es_admin: bool


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: AuthUserSchema
