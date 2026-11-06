
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    CheckConstraint
)

from src.db.connection import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True)

    nombre = Column(
        String(100),
        unique=True,
        nullable=False
    )

    unidad_base = Column(
        String(10),
        nullable=False
    )

    origen_animal = Column(
        Boolean,
        nullable=False,
        default=False
    )

    calorias_por_unidad = Column(
        Float,
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "unidad_base IN ('g', 'ml', 'unidad')",
            name="ck_ingredients_unidad"
        ),
        CheckConstraint(
            "calorias_por_unidad >= 0",
            name="ck_ingredients_calorias"
        ),
    )
