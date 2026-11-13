from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models.receta_model import Recipe
from src.db.models.tutorial_model import Tutorial


class TutorialRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(
        self, categoria: str | None = None, query: str | None = None
    ) -> list[Tutorial]:
        statement = select(Tutorial)
        if categoria is not None:
            statement = statement.where(Tutorial.categoria == categoria)
        if query:
            statement = statement.where(Tutorial.titulo.icontains(query, autoescape=True))
        statement = statement.order_by(Tutorial.orden, Tutorial.id)
        return list(self.db.scalars(statement).all())

    def find_by_id(self, tutorial_id: int) -> Tutorial | None:
        return self.db.get(Tutorial, tutorial_id)

    def find_by_video_url(self, video_url: str) -> Tutorial | None:
        return self.db.scalars(
            select(Tutorial).where(Tutorial.video_url == video_url)
        ).first()

    def create(self, **fields) -> Tutorial:
        tutorial = Tutorial(**fields)
        self.db.add(tutorial)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(tutorial)
        return tutorial

    def find_for_recipe(self, recipe_id: int) -> list[Tutorial]:
        statement = (
            select(Tutorial)
            .where(Tutorial.receta_id == recipe_id)
            .order_by(Tutorial.orden, Tutorial.id)
        )
        return list(self.db.scalars(statement).all())

    def recipe_exists(self, recipe_id: int) -> bool:
        return self.db.get(Recipe, recipe_id) is not None
