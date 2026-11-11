from decimal import Decimal
from typing import Literal

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models.ingrediente_model import Ingredient
from src.db.models.comment_model import Comment
from src.db.models.receta_model import Recipe
from src.db.models.step_model import Step
from src.db.models.recipe_ingredient_model import RecipeIngredient


class RecipeRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all_details(
        self, vegana: bool | None = None, *,
        titulo: str | None = None,
        dificultad: str | None = None,
        tiempo_max: int | None = None,
        ingrediente: str | None = None,
        ordenar_por: Literal["fecha", "puntaje"] | None = None,
    ) -> list[tuple[Recipe, list[RecipeIngredient], list[Step], list[Ingredient]]]:
        animal_ingredient = (
            self.db.query(RecipeIngredient.receta_id)
            .join(Ingredient, Ingredient.id == RecipeIngredient.ingrediente_id)
            .filter(
                RecipeIngredient.receta_id == Recipe.id,
                Ingredient.origen_animal.is_(True),
            )
            .exists()
        )
        query = self.db.query(Recipe)
        if vegana is not None:
            query = query.filter(~animal_ingredient if vegana else animal_ingredient)
        if titulo is not None:
            # autoescape trata % y _ como texto, no como comodines SQL.
            query = query.filter(Recipe.titulo.icontains(titulo, autoescape=True))
        if dificultad is not None:
            query = query.filter(Recipe.dificultad == dificultad)
        if tiempo_max is not None:
            query = query.filter(Recipe.tiempo_min <= tiempo_max)
        if ingrediente is not None:
            matching_ingredient = (
                self.db.query(RecipeIngredient.receta_id)
                .join(Ingredient, Ingredient.id == RecipeIngredient.ingrediente_id)
                .filter(
                    RecipeIngredient.receta_id == Recipe.id,
                    Ingredient.nombre.icontains(ingrediente, autoescape=True),
                ).exists()
            )
            query = query.filter(matching_ingredient)
        if ordenar_por == "puntaje":
            average_score = (
                self.db.query(func.avg(Comment.puntaje))
                .filter(Comment.receta_id == Recipe.id)
                .correlate(Recipe).scalar_subquery()
            )
            query = query.order_by(
                average_score.desc().nullslast(),
                Recipe.fecha_publicacion.desc(), Recipe.id.desc(),
            )
        elif ordenar_por == "fecha":
            query = query.order_by(Recipe.fecha_publicacion.desc(), Recipe.id.desc())
        else:
            # Conservar el orden anterior cuando no se solicita uno explícito.
            query = query.order_by(Recipe.id)
        recipes = query.all()
        return self.load_details(recipes)

    def load_details(
        self, recipes: list[Recipe]
    ) -> list[tuple[Recipe, list[RecipeIngredient], list[Step], list[Ingredient]]]:
        """Carga relaciones por lote y conserva el orden de las recetas recibidas."""
        if not recipes:
            return []

        # Cargar las relaciones por lote evita consultas adicionales por receta.
        recipe_ids = [recipe.id for recipe in recipes]
        relations = (
            self.db.query(RecipeIngredient)
            .filter(RecipeIngredient.receta_id.in_(recipe_ids))
            .order_by(RecipeIngredient.ingrediente_id).all()
        )
        steps = (
            self.db.query(Step).filter(Step.receta_id.in_(recipe_ids))
            .order_by(Step.orden).all()
        )
        ingredient_ids = {row.ingrediente_id for row in relations}
        ingredients = (
            self.db.query(Ingredient).filter(Ingredient.id.in_(ingredient_ids)).all()
        ) if ingredient_ids else []
        ingredient_by_id = {item.id: item for item in ingredients}
        relations_by_recipe = {recipe.id: [] for recipe in recipes}
        steps_by_recipe = {recipe.id: [] for recipe in recipes}
        for row in relations:
            relations_by_recipe[row.receta_id].append(row)
        for step in steps:
            steps_by_recipe[step.receta_id].append(step)
        return [
            (
                recipe,
                relations_by_recipe[recipe.id],
                steps_by_recipe[recipe.id],
                [ingredient_by_id[row.ingrediente_id]
                 for row in relations_by_recipe[recipe.id]],
            )
            for recipe in recipes
        ]

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

    def find_details_by_id(
        self, recipe_id: int
    ) -> tuple[Recipe, list[RecipeIngredient], list[Step], list[Ingredient]] | None:
        recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe is None:
            return None

        recipe_ingredients = (
            self.db.query(RecipeIngredient)
            .filter(RecipeIngredient.receta_id == recipe_id)
            .order_by(RecipeIngredient.ingrediente_id)
            .all()
        )
        steps = (
            self.db.query(Step)
            .filter(Step.receta_id == recipe_id)
            .order_by(Step.orden)
            .all()
        )
        ingredients = (
            self.db.query(Ingredient)
            .filter(Ingredient.id.in_([row.ingrediente_id for row in recipe_ingredients]))
            .order_by(Ingredient.id)
            .all()
        )
        return recipe, recipe_ingredients, steps, ingredients

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
