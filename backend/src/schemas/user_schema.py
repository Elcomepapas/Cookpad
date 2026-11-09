from pydantic import BaseModel, EmailStr, Field


class CreateUserSchema(BaseModel):
    email: EmailStr
    nombre: str
    password: str = Field(min_length=8)


class UpdateUserSchema(BaseModel):
    email: EmailStr | None = None
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
