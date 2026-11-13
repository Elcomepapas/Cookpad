from datetime import datetime
from pydantic import BaseModel


class CreateUserDTO(BaseModel):
    email: str
    nombre: str
    password: str


class UpdateUserDTO(BaseModel):
    email: str | None = None
    nombre: str | None = None


class UserResponseDTO(BaseModel):
    id: int
    email: str
    nombre: str
    fecha_registro: datetime
    es_admin: bool

    model_config = {"from_attributes": True}
