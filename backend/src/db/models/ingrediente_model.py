
from sqlalchemy import Column, Integer, String, Boolean, Numeric, CheckConstraint

from src.db.connection import Base


class Ingredient(Base):
    __tablename__ = "ingrediente"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    unidad_base = Column(String(10), nullable=False)
    origen_animal = Column(Boolean, nullable=False, default=False)
    calorias_por_unidad = Column(Numeric(10, 2), nullable=False, default=0)

    __table_args__ = (
        CheckConstraint(
            "unidad_base IN ('g', 'ml', 'unidad')",
            name="ck_ingrediente_unidad_base"
        ),
        CheckConstraint(
            "calorias_por_unidad >= 0",
            name="ck_ingrediente_calorias"
        ),
    )
