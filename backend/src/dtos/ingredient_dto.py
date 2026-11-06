from pydantic import BaseModel


class IngredientResponseDTO(BaseModel):
    id: int
    nombre: str
    unidad_base: str
    origen_animal: bool
    calorias_por_unidad: float

    model_config = {"from_attributes": True}
