
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from src.db.connection import Base


class User(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    fecha_registro = Column(DateTime, nullable=False, server_default=func.now())

    # Campos que ya utiliza la plantilla del profesor
    password_hash = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    is_admin = Column(Boolean, default=False)
