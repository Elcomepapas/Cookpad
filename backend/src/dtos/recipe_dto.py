from datetime import datetime

from pydantic import BaseModel


class RecipeResponseDTO(BaseModel):
    id: int
    autor_id: int
    titulo: str
    porciones: int
    tiempo_min: int
    dificultad: str
    fecha_publicacion: datetime

    model_config = {"from_attributes": True}
