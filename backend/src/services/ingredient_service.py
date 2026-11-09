from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dtos.ingredient_dto import CreateIngredientDTO, IngredientResponseDTO
from src.mappers.ingredient_mapper import to_ingredient_response
from src.repositories.ingredient_repository import IngredientRepository
from src.utils.errors import ConflictError


class IngredientService:
    def __init__(self, db: Session):
        self.repo = IngredientRepository(db)

    def list_all(self) -> list[IngredientResponseDTO]:
        return [to_ingredient_response(item) for item in self.repo.list_all()]

    def create(self, dto: CreateIngredientDTO) -> IngredientResponseDTO:
        if self.repo.find_by_name(dto.nombre):
            raise ConflictError("An ingredient with this name already exists")

        try:
            ingredient = self.repo.create(
                nombre=dto.nombre,
                unidad_base=dto.unidad_base,
                calorias_por_unidad=dto.calorias_por_unidad,
                origen_animal=dto.origen_animal,
            )
        except IntegrityError as exc:
            # Cubre una creación concurrente posterior a la comprobación previa.
            raise ConflictError("An ingredient with this name already exists") from exc

        return to_ingredient_response(ingredient)
