from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.dtos.weekly_plan_dto import WeeklyPlanResponseDTO
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
        return to_weekly_plan_response(plan, self.repo)

    def get(self, user_id: int, plan_id: int) -> WeeklyPlanResponseDTO:
        plan = self._get_owned_plan(user_id, plan_id)
        return to_weekly_plan_response(plan, self.repo)

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
