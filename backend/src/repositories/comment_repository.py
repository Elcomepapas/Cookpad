from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models.comment_model import Comment
from src.db.models.receta_model import Recipe


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_recipe(self, recipe_id: int) -> Recipe | None:
        return self.db.query(Recipe).filter(Recipe.id == recipe_id).first()

    def find_by_user_and_recipe(self, user_id: int, recipe_id: int) -> Comment | None:
        return self.db.query(Comment).filter(
            Comment.usuario_id == user_id, Comment.receta_id == recipe_id,
        ).first()

    def find_by_id(self, recipe_id: int, comment_id: int) -> Comment | None:
        return self.db.query(Comment).filter(
            Comment.id == comment_id, Comment.receta_id == recipe_id,
        ).first()

    def list_by_recipe(self, recipe_id: int) -> list[Comment]:
        return self.db.query(Comment).filter(Comment.receta_id == recipe_id).order_by(
            Comment.fecha.desc(), Comment.id.desc(),
        ).all()

    def create(self, user_id: int, recipe_id: int, texto: str, puntaje: int) -> Comment:
        comment = Comment(usuario_id=user_id, receta_id=recipe_id,
                          texto=texto, puntaje=puntaje)
        try:
            self.db.add(comment)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(comment)
        return comment

    def update(self, recipe_id: int, comment_id: int, texto: str, puntaje: int) -> Comment | None:
        comment = self.find_by_id(recipe_id, comment_id)
        if comment is None:
            return None
        comment.texto = texto
        comment.puntaje = puntaje
        comment.fecha_edicion = func.now()
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(comment)
        return comment
