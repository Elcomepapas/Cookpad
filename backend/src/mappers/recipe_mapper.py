from src.db.models.recetas_model import Recipe
from src.dtos.recipe_dto import RecipeResponseDTO


def to_recipe_response(recipe: Recipe) -> RecipeResponseDTO:
    """Convierte un Model SQLAlchemy en un DTO de respuesta."""
    return RecipeResponseDTO.model_validate(recipe)
