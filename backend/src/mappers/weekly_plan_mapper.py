from src.db.models.weekly_plan_model import WeeklyPlan
from src.dtos.weekly_plan_dto import WeeklyPlanResponseDTO
from src.repositories.weekly_plan_repository import WeeklyPlanRepository


def to_weekly_plan_response(
    plan: WeeklyPlan, repo: WeeklyPlanRepository
) -> WeeklyPlanResponseDTO:
    return WeeklyPlanResponseDTO(
        id=plan.id,
        usuario_id=plan.usuario_id,
        fecha_inicio=plan.fecha_inicio,
        recetas=repo.list_recipes(plan.id),
    )
