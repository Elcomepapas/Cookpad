from src.db.models.receta_model import Recipe
from src.db.models.ingrediente_model import Ingredient
from src.db.models.recipe_ingredient_model import RecipeIngredient
from src.db.models.step_model import Step
from src.dtos.recipe_dto import (
    RecipeIngredientResponseDTO,
    RecipeResponseDTO,
    StepResponseDTO,
)


def to_recipe_response(
    recipe: Recipe,
    recipe_ingredients: list[RecipeIngredient] | None = None,
    steps: list[Step] | None = None,
    ingredients: list[Ingredient] | None = None,
) -> RecipeResponseDTO:
    """Convierte una receta y sus relaciones cargadas en un DTO de respuesta."""
    ingredient_by_id = {item.id: item for item in ingredients or []}
    ingredient_responses = []
    for recipe_ingredient in recipe_ingredients or []:
        ingredient = ingredient_by_id.get(recipe_ingredient.ingrediente_id)
        if ingredient is None:
            continue
        ingredient_responses.append(
            RecipeIngredientResponseDTO(
                ingrediente_id=ingredient.id,
                nombre=ingredient.nombre,
                unidad_base=ingredient.unidad_base,
                cantidad=float(recipe_ingredient.cantidad),
            )
        )

    response = RecipeResponseDTO.model_validate(recipe)
    return response.model_copy(
        update={
            "ingredientes": ingredient_responses,
            "pasos": [
                StepResponseDTO.model_validate(step)
                for step in sorted(steps or [], key=lambda item: item.orden)
            ],
        }
    )
