from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CreateWeeklyPlanSchema(BaseModel):
    fecha_inicio: date

    model_config = {"extra": "forbid"}

    @field_validator("fecha_inicio")
    @classmethod
    def require_monday(cls, value: date) -> date:
        if value.weekday() != 0:
            raise ValueError("La fecha de inicio del plan debe ser lunes")
        return value


class AddPlanRecipeSchema(BaseModel):
    receta_id: int = Field(gt=0)
    dia_semana: int = Field(ge=1, le=7)
    comida: Literal["desayuno", "almuerzo", "merienda", "cena"]
    porciones: int = Field(gt=0)

    model_config = {"extra": "forbid"}
