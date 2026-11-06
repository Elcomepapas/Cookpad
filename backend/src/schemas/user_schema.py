from pydantic import BaseModel, EmailStr, Field


class CreateUserSchema(BaseModel):
    email: EmailStr
    nombre: str
    password: str = Field(min_length=8)


class UpdateUserSchema(BaseModel):
    # TODO: completar con los campos opcionales que se permiten actualizar.
    # Tip: todos los campos van como Optional / con default None.
    ...
