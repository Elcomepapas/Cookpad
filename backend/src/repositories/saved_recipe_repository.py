from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models.ingrediente_model import Ingredient
from src.db.models.receta_model import Recipe
from src.db.models.recipe_ingredient_model import RecipeIngredient
from src.db.models.saved_recipe_model import SavedRecipe
from src.db.models.step_model import Step
from src.repositories.recipe_repository import RecipeRepository


class SavedRecipeRepository:
    def __init__(self, db: Session):
        self.db = db

    def recipe_exists(self, recipe_id: int) -> bool:
        return self.db.query(Recipe.id).filter(Recipe.id == recipe_id).first() is not None

    def find(self, user_id: int, recipe_id: int) -> SavedRecipe | None:
        return self.db.get(SavedRecipe, (user_id, recipe_id))

    def create(self, user_id: int, recipe_id: int) -> SavedRecipe:
        saved = SavedRecipe(usuario_id=user_id, receta_id=recipe_id)
        try:
            self.db.add(saved)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(saved)
        return saved

    def list_details(self, user_id: int) -> list[
        tuple[SavedRecipe, tuple[Recipe, list[RecipeIngredient], list[Step], list[Ingredient]]]
    ]:
        rows = (
            self.db.query(SavedRecipe, Recipe)
            .join(Recipe, Recipe.id == SavedRecipe.receta_id)
            .filter(SavedRecipe.usuario_id == user_id)
            .order_by(SavedRecipe.fecha.desc(), SavedRecipe.receta_id.desc())
            .all()
        )
        details = RecipeRepository(self.db).load_details([recipe for _, recipe in rows])
        return [(row[0], detail) for row, detail in zip(rows, details)]
