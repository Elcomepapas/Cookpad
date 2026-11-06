
from sqlalchemy import Column, Integer, Numeric, ForeignKey, CheckConstraint

from src.db.connection import Base


class RecipeIngredient(Base):
    __tablename__ = "receta_ingredientes"

    receta_id = Column(
        Integer,
        ForeignKey("receta.id", ondelete="CASCADE"),
        primary_key=True
    )

    ingrediente_id = Column(
        Integer,
        ForeignKey("ingrediente.id", ondelete="RESTRICT"),
        primary_key=True
    )

    cantidad = Column(Numeric(10, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_ri_cantidad"),
    )
