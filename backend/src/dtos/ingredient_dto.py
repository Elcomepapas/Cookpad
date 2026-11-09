from decimal import Decimal

from pydantic import BaseModel


class CreateIngredientDTO(BaseModel):
    nombre: str
    unidad_base: str
    origen_animal: bool = False
    calorias_por_unidad: Decimal


class IngredientResponseDTO(BaseModel):
    id: int
    nombre: str
    unidad_base: str
    origen_animal: bool
    calorias_por_unidad: float

    model_config = {"from_attributes": True}
