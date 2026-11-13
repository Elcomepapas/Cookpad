
from sqlalchemy import (
    Column, Integer, Date, ForeignKey,
    UniqueConstraint, CheckConstraint
)

from src.db.connection import Base


class WeeklyPlan(Base):
    __tablename__ = "plan_semanal"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    fecha_inicio = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "usuario_id", "fecha_inicio",
            name="uq_plan_usuario_semana"
        ),
        CheckConstraint(
            "EXTRACT(ISODOW FROM fecha_inicio) = 1",
            name="ck_plan_inicio_lunes"
        ).ddl_if(dialect="postgresql"),
    )
