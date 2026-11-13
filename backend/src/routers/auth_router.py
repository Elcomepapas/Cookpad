from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.dtos.auth_dto import LoginDTO, TokenDTO
from src.dtos.user_dto import CreateUserDTO, UserResponseDTO
from src.schemas.auth_schema import LoginSchema, TokenSchema
from src.schemas.user_schema import CreateUserSchema
from src.services.auth_service import AuthService
from src.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponseDTO, status_code=201)
def register(payload: CreateUserSchema, db: Session = Depends(get_db)):
    dto = CreateUserDTO(**payload.model_dump())
    return UserService(db).create(dto)


@router.post("/login", response_model=TokenSchema)
def login(payload: LoginSchema, db: Session = Depends(get_db)):
    dto = LoginDTO(**payload.model_dump())
    token: TokenDTO = AuthService(db).login(dto)
    return TokenSchema(**token.model_dump())
