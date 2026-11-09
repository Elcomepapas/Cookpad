
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func

from src.db.connection import Base


class User(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    fecha_registro = Column(DateTime, nullable=False, server_default=func.now())

    password_hash = Column(String, nullable=False)
    es_admin = Column(Boolean, nullable=False, default=False, server_default="false")
