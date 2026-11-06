from src.db.models.ingredient_model import Ingredient
from src.dtos.ingredient_dto import IngredientResponseDTO


def to_ingredient_response(ingredient: Ingredient) -> IngredientResponseDTO:
    """Convierte un Model SQLAlchemy en un DTO de respuesta."""
    return IngredientResponseDTO.model_validate(ingredient)
