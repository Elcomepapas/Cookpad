from pydantic import BaseModel

from src.dtos.user_dto import UserResponseDTO


class LoginDTO(BaseModel):
    email: str
    password: str


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UserResponseDTO
