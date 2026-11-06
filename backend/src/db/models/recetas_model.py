
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint
)
from sqlalchemy.sql import func

from src.db.connection import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)

    autor_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    titulo = Column(String(200), nullable=False)

    porciones = Column(Integer, nullable=False)

    tiempo_min = Column(Integer, nullable=False)

    dificultad = Column(String(10), nullable=False)

    fecha_publicacion = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "autor_id", "titulo",
            name="uq_recipes_autor_titulo"
        ),
        CheckConstraint(
            "porciones > 0",
            name="ck_recipes_porciones"
        ),
        CheckConstraint(
            "tiempo_min > 0",
            name="ck_recipes_tiempo"
        ),
        CheckConstraint(
            "dificultad IN ('facil', 'media', 'dificil')",
            name="ck_recipes_dificultad"
        ),
    )
