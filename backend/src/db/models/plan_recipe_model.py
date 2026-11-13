from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)

from src.db.connection import Base


class PlanRecipe(Base):
    __tablename__ = "plan_recetas"

    id = Column(Integer, primary_key=True)
    plan_id = Column(
        Integer, ForeignKey("plan_semanal.id", ondelete="CASCADE"), nullable=False
    )
    receta_id = Column(
        Integer, ForeignKey("receta.id", ondelete="CASCADE"), nullable=False
    )
    dia_semana = Column(Integer, nullable=False)
    comida = Column(String(10), nullable=False)
    porciones = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "plan_id", "dia_semana", "comida", name="uq_pr_dia_comida"
        ),
        CheckConstraint("dia_semana BETWEEN 1 AND 7", name="ck_pr_dia"),
        CheckConstraint(
            "comida IN ('desayuno', 'almuerzo', 'merienda', 'cena')",
            name="ck_pr_comida",
        ),
        CheckConstraint("porciones > 0", name="ck_pr_porciones"),
    )
