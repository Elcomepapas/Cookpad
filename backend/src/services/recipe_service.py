from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dtos.recipe_dto import CreateRecipeDTO, RecipeResponseDTO, SearchRecipeDTO
from src.mappers.recipe_mapper import to_recipe_response
from src.repositories.recipe_repository import RecipeRepository
from src.utils.errors import ConflictError, NotFoundError


class RecipeService:
    def __init__(self, db: Session):
        self.repo = RecipeRepository(db)

    def list_all(self, filters: SearchRecipeDTO) -> list[RecipeResponseDTO]:
        details = self.repo.find_all_details(**filters.model_dump())
        return [to_recipe_response(*recipe) for recipe in details]

    def find_using_only(self, ingredient_ids: list[int]) -> list[RecipeResponseDTO]:
        details = self.repo.find_recipes_using_only(ingredient_ids)
        return [to_recipe_response(*recipe) for recipe in details]

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

    def get_by_id(
        self, recipe_id: int, requested_servings: int | None = None
    ) -> RecipeResponseDTO:
        details = self.repo.find_details_by_id(recipe_id)
        if details is None:
            raise NotFoundError("Recipe not found")

        recipe, _, _, _ = details
        servings = requested_servings or recipe.porciones
        return to_recipe_response(*details, servings=servings)
