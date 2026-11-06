from sqlalchemy.orm import Session

from src.db.models.usuario_model import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, nombre: str, password_hash: str) -> User:
        user = User(email=email, nombre=nombre, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def find_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def find_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def list_all(self) -> list[User]:
        # TODO: devolver todos los usuarios
        ...

    def update(self, user_id: int, **fields) -> User | None:
        # TODO: actualizar los campos pasados en **fields y devolver el User actualizado
        ...

    def delete(self, user_id: int) -> bool:
        # TODO: borrar el User con ese id; devolver True si lo borró, False si no existía
        ...
