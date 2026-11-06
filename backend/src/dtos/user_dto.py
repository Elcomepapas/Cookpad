from datetime import datetime
from pydantic import BaseModel


class CreateUserDTO(BaseModel):
    email: str
    nombre: str
    password: str


class UserResponseDTO(BaseModel):
    id: int
    email: str
    nombre: str
    fecha_registro: datetime

    model_config = {"from_attributes": True}
