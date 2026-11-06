
from sqlalchemy import (
    Column, Integer, String, DateTime,
    ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.sql import func

from src.db.connection import Base


class Recipe(Base):
    __tablename__ = "receta"

    id = Column(Integer, primary_key=True)
    autor_id = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    titulo = Column(String(200), nullable=False)
    porciones = Column(Integer, nullable=False)
    tiempo_min = Column(Integer, nullable=False)
    dificultad = Column(String(10), nullable=False)
    fecha_publicacion = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("autor_id", "titulo", name="uq_receta_autor_titulo"),
        CheckConstraint("porciones > 0", name="ck_receta_porciones"),
        CheckConstraint("tiempo_min > 0", name="ck_receta_tiempo"),
        CheckConstraint(
            "dificultad IN ('facil', 'media', 'dificil')",
            name="ck_receta_dificultad"
        ),
    )
