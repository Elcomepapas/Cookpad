
from sqlalchemy import (
    Column, Integer, Text, DateTime,
    ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.sql import func

from src.db.connection import Base


class Comment(Base):
    __tablename__ = "comentario"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    receta_id = Column(Integer, ForeignKey("receta.id", ondelete="CASCADE"), nullable=False)
    texto = Column(Text, nullable=False)
    puntaje = Column(Integer, nullable=False)
    fecha = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "usuario_id", "receta_id",
            name="uq_comentario_usuario_receta"
        ),
        CheckConstraint(
            "puntaje BETWEEN 1 AND 5",
            name="ck_comentario_puntaje"
        ),
    )
