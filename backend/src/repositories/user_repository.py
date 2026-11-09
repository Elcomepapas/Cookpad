from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models.usuario_model import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, nombre: str, password_hash: str) -> User:
        user = User(email=email, nombre=nombre, password_hash=password_hash)
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(user)
        return user

    def find_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def find_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def list_all(self) -> list[User]:
        return self.db.query(User).order_by(User.id).all()

    def update(self, user_id: int, **fields) -> User | None:
        user = self.find_by_id(user_id)
        if user is None:
            return None

        for field, value in fields.items():
            if field not in {"email", "nombre"}:
                raise ValueError(f"Unsupported user field: {field}")
            setattr(user, field, value)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.find_by_id(user_id)
        if user is None:
            return False

        self.db.delete(user)
        self.db.commit()
        return True
