from decimal import Decimal, ROUND_HALF_UP

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
    servings: int | None = None,
) -> RecipeResponseDTO:
    """Convierte una receta y sus relaciones cargadas en un DTO de respuesta."""
    target_servings = servings or recipe.porciones
    scale = Decimal(target_servings) / Decimal(recipe.porciones)
    ingredient_by_id = {item.id: item for item in ingredients or []}
    ingredient_responses = []
    total_calories = Decimal("0")
    for recipe_ingredient in recipe_ingredients or []:
        ingredient = ingredient_by_id.get(recipe_ingredient.ingrediente_id)
        if ingredient is None:
            continue
        scaled_quantity = (Decimal(recipe_ingredient.cantidad) * scale).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total_calories += Decimal(ingredient.calorias_por_unidad) * scaled_quantity
        ingredient_responses.append(
            RecipeIngredientResponseDTO(
                ingrediente_id=ingredient.id,
                nombre=ingredient.nombre,
                unidad_base=ingredient.unidad_base,
                cantidad=float(scaled_quantity),
            )
        )

    response = RecipeResponseDTO.model_validate(recipe)
    return response.model_copy(
        update={
            "porciones": target_servings,
            "ingredientes": ingredient_responses,
            "pasos": [
                StepResponseDTO.model_validate(step)
                for step in sorted(steps or [], key=lambda item: item.orden)
            ],
            "calorias_totales": float(
                total_calories.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "calorias_por_porcion": float(
                (total_calories / Decimal(target_servings)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            ),
        }
    )
