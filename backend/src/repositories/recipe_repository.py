from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models.ingrediente_model import Ingredient
from src.db.models.receta_model import Recipe
from src.db.models.step_model import Step
from src.db.models.recipe_ingredient_model import RecipeIngredient


class RecipeRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_author_and_title(self, author_id: int, title: str) -> Recipe | None:
        return (
            self.db.query(Recipe)
            .filter(Recipe.autor_id == author_id, Recipe.titulo == title)
            .first()
        )

    def find_ingredient_ids(self, ingredient_ids: list[int]) -> set[int]:
        rows = (
            self.db.query(Ingredient.id)
            .filter(Ingredient.id.in_(ingredient_ids))
            .all()
        )
        return {row[0] for row in rows}

    def create(
        self,
        *,
        author_id: int,
        title: str,
        servings: int,
        time_min: int,
        difficulty: str,
        recipe_ingredients: list[tuple[int, Decimal]],
        steps: list[tuple[int, str]],
    ) -> tuple[Recipe, list[RecipeIngredient], list[Step], list[Ingredient]]:
        recipe = Recipe(
            autor_id=author_id,
            titulo=title,
            porciones=servings,
            tiempo_min=time_min,
            dificultad=difficulty,
        )
        try:
            self.db.add(recipe)
            self.db.flush()

            relation_rows = [
                RecipeIngredient(
                    receta_id=recipe.id,
                    ingrediente_id=ingredient_id,
                    cantidad=quantity,
                )
                for ingredient_id, quantity in recipe_ingredients
            ]
            step_rows = [
                Step(receta_id=recipe.id, orden=order, descripcion=description)
                for order, description in steps
            ]
            self.db.add_all([*relation_rows, *step_rows])
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise

        self.db.refresh(recipe)
        saved_relations = (
            self.db.query(RecipeIngredient)
            .filter(RecipeIngredient.receta_id == recipe.id)
            .order_by(RecipeIngredient.ingrediente_id)
            .all()
        )
        saved_steps = (
            self.db.query(Step)
            .filter(Step.receta_id == recipe.id)
            .order_by(Step.orden)
            .all()
        )
        saved_ingredients = (
            self.db.query(Ingredient)
            .filter(Ingredient.id.in_([row.ingrediente_id for row in saved_relations]))
            .order_by(Ingredient.id)
            .all()
        )
        return recipe, saved_relations, saved_steps, saved_ingredients
