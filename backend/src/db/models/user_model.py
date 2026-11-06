from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from src.db.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(String, unique=True, nullable=False)

    nombre = Column(String(100), nullable=False)

    password_hash = Column(String, nullable=False)

    age = Column(Integer, nullable=False)

    is_admin = Column(Boolean, default=False)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
