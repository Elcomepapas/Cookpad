from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dtos.tutorial_dto import CreateTutorialDTO, TutorialResponseDTO
from src.repositories.tutorial_repository import TutorialRepository
from src.utils.errors import ConflictError, NotFoundError


class TutorialService:
    def __init__(self, db: Session):
        self.repository = TutorialRepository(db)

    def list_all(
        self, categoria: str | None = None, query: str | None = None
    ) -> list[TutorialResponseDTO]:
        return [
            TutorialResponseDTO.model_validate(tutorial)
            for tutorial in self.repository.find_all(categoria, query)
        ]

    def get_by_id(self, tutorial_id: int) -> TutorialResponseDTO:
        tutorial = self.repository.find_by_id(tutorial_id)
        if tutorial is None:
            raise NotFoundError("Tutorial not found")
        return TutorialResponseDTO.model_validate(tutorial)

    def list_for_recipe(self, recipe_id: int) -> list[TutorialResponseDTO]:
        if not self.repository.recipe_exists(recipe_id):
            raise NotFoundError("Recipe not found")
        return [
            TutorialResponseDTO.model_validate(tutorial)
            for tutorial in self.repository.find_for_recipe(recipe_id)
        ]

    def create(self, dto: CreateTutorialDTO) -> TutorialResponseDTO:
        if self.repository.find_by_video_url(dto.video_url):
            raise ConflictError("A tutorial with this video URL already exists")
        if dto.receta_id is not None and not self.repository.recipe_exists(dto.receta_id):
            raise NotFoundError("Recipe not found")

        try:
            tutorial = self.repository.create(**dto.model_dump())
        except IntegrityError as exc:
            raise ConflictError("A tutorial with this video URL already exists") from exc
        return TutorialResponseDTO.model_validate(tutorial)
