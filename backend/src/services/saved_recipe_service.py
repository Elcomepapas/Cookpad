from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dtos.saved_recipe_dto import (
    SaveRecipeDTO, SavedRecipeDetailsDTO, SavedRecipeResponseDTO,
)
from src.mappers.saved_recipe_mapper import to_saved_recipe_details, to_saved_recipe_response
from src.repositories.saved_recipe_repository import SavedRecipeRepository
from src.utils.errors import ConflictError, NotFoundError


class SavedRecipeService:
    def __init__(self, db: Session):
        self.repo = SavedRecipeRepository(db)

    def save(self, user_id: int, dto: SaveRecipeDTO) -> SavedRecipeResponseDTO:
        if not self.repo.recipe_exists(dto.receta_id):
            raise NotFoundError("Recipe not found")
        if self.repo.find(user_id, dto.receta_id) is not None:
            raise ConflictError("Recipe already saved")
        try:
            saved = self.repo.create(user_id, dto.receta_id)
        except IntegrityError as exc:
            # La PK compuesta protege también frente a dos solicitudes simultáneas.
            if self.repo.find(user_id, dto.receta_id) is not None:
                raise ConflictError("Recipe already saved") from exc
            if not self.repo.recipe_exists(dto.receta_id):
                raise NotFoundError("Recipe not found") from exc
            raise
        return to_saved_recipe_response(saved)

    def list_saved(self, user_id: int) -> list[SavedRecipeDetailsDTO]:
        return [to_saved_recipe_details(saved, details)
                for saved, details in self.repo.list_details(user_id)]
