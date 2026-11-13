from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models.ingrediente_model import Ingredient
from src.db.models.plan_recipe_model import PlanRecipe
from src.db.models.receta_model import Recipe
from src.db.models.recipe_ingredient_model import RecipeIngredient
from src.db.models.weekly_plan_model import WeeklyPlan


class WeeklyPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_user_and_date(
        self, user_id: int, start_date: date
    ) -> WeeklyPlan | None:
        return (
            self.db.query(WeeklyPlan)
            .filter(
                WeeklyPlan.usuario_id == user_id,
                WeeklyPlan.fecha_inicio == start_date,
            )
            .first()
        )

    def find_by_id(self, plan_id: int) -> WeeklyPlan | None:
        return self.db.query(WeeklyPlan).filter(WeeklyPlan.id == plan_id).first()

    def create(self, user_id: int, start_date: date) -> WeeklyPlan:
        plan = WeeklyPlan(usuario_id=user_id, fecha_inicio=start_date)
        try:
            self.db.add(plan)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(plan)
        return plan

    def list_recipes(self, plan_id: int) -> list[PlanRecipe]:
        return (
            self.db.query(PlanRecipe)
            .filter(PlanRecipe.plan_id == plan_id)
            .order_by(PlanRecipe.dia_semana, PlanRecipe.comida, PlanRecipe.id)
            .all()
        )

    def recipe_exists(self, recipe_id: int) -> bool:
        return self.db.query(Recipe.id).filter(Recipe.id == recipe_id).first() is not None

    def find_slot(
        self, plan_id: int, day: int, meal: str
    ) -> PlanRecipe | None:
        return (
            self.db.query(PlanRecipe)
            .filter(
                PlanRecipe.plan_id == plan_id,
                PlanRecipe.dia_semana == day,
                PlanRecipe.comida == meal,
            )
            .first()
        )

    def add_recipe(
        self,
        plan_id: int,
        recipe_id: int,
        day: int,
        meal: str,
        servings: int,
    ) -> PlanRecipe:
        entry = PlanRecipe(
            plan_id=plan_id,
            receta_id=recipe_id,
            dia_semana=day,
            comida=meal,
            porciones=servings,
        )
        try:
            self.db.add(entry)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(entry)
        return entry

    def delete_recipe(self, entry: PlanRecipe) -> None:
        self.db.delete(entry)
        self.db.commit()

    def find_plan_recipe(self, plan_id: int, entry_id: int) -> PlanRecipe | None:
        return (
            self.db.query(PlanRecipe)
            .filter(PlanRecipe.plan_id == plan_id, PlanRecipe.id == entry_id)
            .first()
        )

    def list_shopping_ingredients(self, plan_id: int) -> list[
        tuple[PlanRecipe, Recipe, RecipeIngredient, Ingredient]
    ]:
        return (
            self.db.query(PlanRecipe, Recipe, RecipeIngredient, Ingredient)
            .join(Recipe, Recipe.id == PlanRecipe.receta_id)
            .join(RecipeIngredient, RecipeIngredient.receta_id == Recipe.id)
            .join(Ingredient, Ingredient.id == RecipeIngredient.ingrediente_id)
            .filter(PlanRecipe.plan_id == plan_id)
            .order_by(Ingredient.nombre, Ingredient.id, PlanRecipe.id)
            .all()
        )
