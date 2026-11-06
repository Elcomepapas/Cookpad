
from sqlalchemy import (
    Column, Integer, Text, ForeignKey,
    UniqueConstraint, CheckConstraint
)

from src.db.connection import Base


class Step(Base):
    __tablename__ = "paso"

    id = Column(Integer, primary_key=True)
    receta_id = Column(Integer, ForeignKey("receta.id", ondelete="CASCADE"), nullable=False)
    orden = Column(Integer, nullable=False)
    descripcion = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("receta_id", "orden", name="uq_paso_receta_orden"),
        CheckConstraint("orden >= 1", name="ck_paso_orden"),
    )
