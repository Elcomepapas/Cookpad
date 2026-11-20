from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dtos.weekly_plan_dto import DailyCaloriesDTO, ShoppingListItemDTO, WeeklyPlanResponseDTO
from src.mappers.recipe_mapper import round_recipe_value, scale_recipe_quantity
from src.mappers.weekly_plan_mapper import to_weekly_plan_response
from src.repositories.weekly_plan_repository import WeeklyPlanRepository
from src.utils.errors import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)


class WeeklyPlanService:
    def __init__(self, db: Session):
        self.repo = WeeklyPlanRepository(db)

    def create(self, user_id: int, start_date: date) -> WeeklyPlanResponseDTO:
        if start_date.weekday() != 0:
            raise BadRequestError("The plan start date must be a Monday")
        if self.repo.find_by_user_and_date(user_id, start_date) is not None:
            raise ConflictError("A plan already exists for this week")
        try:
            plan = self.repo.create(user_id, start_date)
        except IntegrityError as exc:
            if self.repo.find_by_user_and_date(user_id, start_date) is not None:
                raise ConflictError("A plan already exists for this week") from exc
            raise
        return to_weekly_plan_response(plan, self.repo.list_recipes(plan.id))

    def get(self, user_id: int, plan_id: int) -> WeeklyPlanResponseDTO:
        plan = self._get_owned_plan(user_id, plan_id)
        return to_weekly_plan_response(plan, self.repo.list_recipes(plan.id))

    def list_for_user(self, current_user_id: int, user_id: int) -> list[WeeklyPlanResponseDTO]:
        if current_user_id != user_id:
            raise ForbiddenError("You can only access your own weekly plans")
        return [
            to_weekly_plan_response(plan, entries)
            for plan, entries in self.repo.list_for_user(user_id)
        ]

    def daily_calories(self, user_id: int, plan_id: int) -> list[DailyCaloriesDTO]:
        self._get_owned_plan(user_id, plan_id)
        by_meal: dict[tuple[int, int], Decimal] = defaultdict(Decimal)
        for entry, recipe, recipe_ingredient, ingredient in self.repo.list_shopping_ingredients(plan_id):
            scale = Decimal(entry.porciones) / Decimal(recipe.porciones)
            quantity = scale_recipe_quantity(recipe_ingredient.cantidad, scale)
            by_meal[entry.dia_semana, entry.id] += quantity * Decimal(ingredient.calorias_por_unidad)

        by_day: dict[int, Decimal] = defaultdict(Decimal)
        for (day, _), calories in by_meal.items():
            by_day[day] += round_recipe_value(calories)

        return [DailyCaloriesDTO(dia_semana=day, calorias=float(by_day[day])) for day in range(1, 8)]

    def shopping_list(self, user_id: int, plan_id: int) -> list[ShoppingListItemDTO]:
        self._get_owned_plan(user_id, plan_id)
        totals: dict[int, tuple[str, str, Decimal]] = {}
        for plan_recipe, recipe, recipe_ingredient, ingredient in (
            self.repo.list_shopping_ingredients(plan_id)
        ):
            scaled_quantity = (
                Decimal(recipe_ingredient.cantidad)
                * Decimal(plan_recipe.porciones)
                / Decimal(recipe.porciones)
            )
            if ingredient.id in totals:
                name, unit, quantity = totals[ingredient.id]
                totals[ingredient.id] = (name, unit, quantity + scaled_quantity)
            else:
                totals[ingredient.id] = (
                    ingredient.nombre,
                    ingredient.unidad_base,
                    scaled_quantity,
                )

        return [
            ShoppingListItemDTO(
                ingrediente_id=ingredient_id,
                nombre=name,
                unidad_base=unit,
                cantidad=float(quantity.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            )
            for ingredient_id, (name, unit, quantity) in sorted(
                totals.items(), key=lambda item: (item[1][0].casefold(), item[0])
            )
        ]

    def add_recipe(
        self,
        user_id: int,
        plan_id: int,
        recipe_id: int,
        day: int,
        meal: str,
        servings: int,
    ) -> WeeklyPlanResponseDTO:
        self._get_owned_plan(user_id, plan_id)
        if not self.repo.recipe_exists(recipe_id):
            raise NotFoundError("Recipe not found")
        if self.repo.find_slot(plan_id, day, meal) is not None:
            raise ConflictError("This day and meal already have a recipe")
        try:
            self.repo.add_recipe(plan_id, recipe_id, day, meal, servings)
        except IntegrityError as exc:
            if self.repo.find_slot(plan_id, day, meal) is not None:
                raise ConflictError("This day and meal already have a recipe") from exc
            if not self.repo.recipe_exists(recipe_id):
                raise NotFoundError("Recipe not found") from exc
            raise
        return self.get(user_id, plan_id)

    def remove_recipe(
        self, user_id: int, plan_id: int, entry_id: int
    ) -> WeeklyPlanResponseDTO:
        self._get_owned_plan(user_id, plan_id)
        entry = self.repo.find_plan_recipe(plan_id, entry_id)
        if entry is None:
            raise NotFoundError("Plan recipe not found")
        self.repo.delete_recipe(entry)
        return self.get(user_id, plan_id)

    def _get_owned_plan(self, user_id: int, plan_id: int):
        plan = self.repo.find_by_id(plan_id)
        if plan is None:
            raise NotFoundError("Weekly plan not found")
        if plan.usuario_id != user_id:
            raise ForbiddenError("You can only manage your own weekly plans")
        return plan
