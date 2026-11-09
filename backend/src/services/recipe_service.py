from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dtos.recipe_dto import CreateRecipeDTO, RecipeResponseDTO
from src.mappers.recipe_mapper import to_recipe_response
from src.repositories.recipe_repository import RecipeRepository
from src.utils.errors import ConflictError, NotFoundError


class RecipeService:
    def __init__(self, db: Session):
        self.repo = RecipeRepository(db)

    def create(self, author_id: int, dto: CreateRecipeDTO) -> RecipeResponseDTO:
        if self.repo.find_by_author_and_title(author_id, dto.titulo):
            raise ConflictError("You already have a recipe with this title")

        ingredient_ids = [item.ingrediente_id for item in dto.ingredientes]
        existing_ids = self.repo.find_ingredient_ids(ingredient_ids)
        missing_ids = sorted(set(ingredient_ids) - existing_ids)
        if missing_ids:
            raise NotFoundError(f"Ingredients not found: {missing_ids}")

        try:
            result = self.repo.create(
                author_id=author_id,
                title=dto.titulo,
                servings=dto.porciones,
                time_min=dto.tiempo_min,
                difficulty=dto.dificultad,
                recipe_ingredients=[
                    (item.ingrediente_id, item.cantidad)
                    for item in dto.ingredientes
                ],
                steps=[(step.orden, step.descripcion) for step in dto.pasos],
            )
        except IntegrityError as exc:
            # Puede ocurrir si otra solicitud crea el mismo título en paralelo.
            raise ConflictError(
                "Recipe conflicts with existing data; check its title and ingredients"
            ) from exc

        return to_recipe_response(*result)
