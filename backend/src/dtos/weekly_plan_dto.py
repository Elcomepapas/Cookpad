from datetime import date

from pydantic import BaseModel, Field


class PlanRecipeResponseDTO(BaseModel):
    id: int
    receta_id: int
    dia_semana: int
    comida: str
    porciones: int

    model_config = {"from_attributes": True}


class WeeklyPlanResponseDTO(BaseModel):
    id: int
    usuario_id: int
    fecha_inicio: date
    recetas: list[PlanRecipeResponseDTO] = Field(default_factory=list)

    model_config = {"from_attributes": True}
