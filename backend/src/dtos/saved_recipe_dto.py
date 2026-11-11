from datetime import datetime

from pydantic import BaseModel

from src.dtos.recipe_dto import RecipeResponseDTO


class SaveRecipeDTO(BaseModel):
    receta_id: int


class SavedRecipeResponseDTO(BaseModel):
    usuario_id: int
    receta_id: int
    fecha: datetime

    model_config = {"from_attributes": True}


class SavedRecipeDetailsDTO(RecipeResponseDTO):
    fecha_guardado: datetime
