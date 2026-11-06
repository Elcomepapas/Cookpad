
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func

from src.db.connection import Base


class SavedRecipe(Base):
    __tablename__ = "recetas_guardadas"

    usuario_id = Column(
        Integer,
        ForeignKey("usuario.id", ondelete="CASCADE"),
        primary_key=True
    )

    receta_id = Column(
        Integer,
        ForeignKey("receta.id", ondelete="CASCADE"),
        primary_key=True
    )

    fecha = Column(DateTime, nullable=False, server_default=func.now())
