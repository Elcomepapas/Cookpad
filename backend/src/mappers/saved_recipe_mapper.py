from src.db.models.saved_recipe_model import SavedRecipe
from src.dtos.saved_recipe_dto import SavedRecipeDetailsDTO, SavedRecipeResponseDTO
from src.mappers.recipe_mapper import to_recipe_response


def to_saved_recipe_response(saved: SavedRecipe) -> SavedRecipeResponseDTO:
    return SavedRecipeResponseDTO.model_validate(saved)


def to_saved_recipe_details(saved: SavedRecipe, details: tuple) -> SavedRecipeDetailsDTO:
    recipe = to_recipe_response(*details)
    return SavedRecipeDetailsDTO(**recipe.model_dump(), fecha_guardado=saved.fecha)
