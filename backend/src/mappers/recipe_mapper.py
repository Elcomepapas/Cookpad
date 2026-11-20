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


def round_recipe_value(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def scale_recipe_quantity(quantity: Decimal, scale: Decimal) -> Decimal:
    return round_recipe_value(Decimal(quantity) * scale)


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
        scaled_quantity = scale_recipe_quantity(recipe_ingredient.cantidad, scale)
        total_calories += Decimal(ingredient.calorias_por_unidad) * scaled_quantity
        ingredient_responses.append(
            RecipeIngredientResponseDTO(
                ingrediente_id=ingredient.id,
                nombre=ingredient.nombre,
                unidad_base=ingredient.unidad_base,
                cantidad=float(scaled_quantity),
            )
        )

    es_vegana = not any(item.origen_animal for item in ingredients or [])
    response = RecipeResponseDTO.model_validate(
        {name: getattr(recipe, name) for name in (
            "id", "autor_id", "titulo", "porciones", "tiempo_min",
            "dificultad", "fecha_publicacion",
        )} | {"es_vegana": es_vegana}
    )
    return response.model_copy(
        update={
            "porciones": target_servings,
            "ingredientes": ingredient_responses,
            "pasos": [
                StepResponseDTO.model_validate(step)
                for step in sorted(steps or [], key=lambda item: item.orden)
            ],
            "calorias_totales": float(
                round_recipe_value(total_calories)
            ),
            "calorias_por_porcion": float(
                (total_calories / Decimal(target_servings)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            ),
        }
    )
