from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dtos.comment_dto import CommentDTO, CommentResponseDTO
from src.mappers.comment_mapper import to_comment_response
from src.repositories.comment_repository import CommentRepository
from src.utils.errors import ConflictError, ForbiddenError, NotFoundError


class CommentService:
    def __init__(self, db: Session):
        self.repo = CommentRepository(db)

    def create(self, user_id: int, recipe_id: int, dto: CommentDTO) -> CommentResponseDTO:
        recipe = self.repo.find_recipe(recipe_id)
        if recipe is None:
            raise NotFoundError("Recipe not found")
        if recipe.autor_id == user_id:
            raise ForbiddenError("You cannot rate your own recipe")
        if self.repo.find_by_user_and_recipe(user_id, recipe_id) is not None:
            raise ConflictError("You already commented on this recipe; edit your comment")
        try:
            comment = self.repo.create(user_id, recipe_id, dto.texto, dto.puntaje)
        except IntegrityError as exc:
            # La restricción UNIQUE cubre también solicitudes simultáneas.
            if self.repo.find_by_user_and_recipe(user_id, recipe_id) is not None:
                raise ConflictError("You already commented on this recipe; edit your comment") from exc
            if self.repo.find_recipe(recipe_id) is None:
                raise NotFoundError("Recipe not found") from exc
            raise
        return to_comment_response(comment)

    def update(self, user_id: int, recipe_id: int, comment_id: int,
               dto: CommentDTO) -> CommentResponseDTO:
        recipe = self.repo.find_recipe(recipe_id)
        if recipe is None:
            raise NotFoundError("Recipe not found")
        comment = self.repo.find_by_id(recipe_id, comment_id)
        if comment is None:
            raise NotFoundError("Comment not found")
        if comment.usuario_id != user_id:
            raise ForbiddenError("You can only edit your own comment")
        if recipe.autor_id == user_id:
            raise ForbiddenError("You cannot rate your own recipe")
        updated = self.repo.update(recipe_id, comment_id, dto.texto, dto.puntaje)
        if updated is None:
            raise NotFoundError("Comment not found")
        return to_comment_response(updated)

    def list_by_recipe(self, recipe_id: int) -> list[CommentResponseDTO]:
        if self.repo.find_recipe(recipe_id) is None:
            raise NotFoundError("Recipe not found")
        return [to_comment_response(comment) for comment in self.repo.list_by_recipe(recipe_id)]
