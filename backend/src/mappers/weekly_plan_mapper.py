from src.db.models.plan_recipe_model import PlanRecipe
from src.db.models.weekly_plan_model import WeeklyPlan
from src.dtos.weekly_plan_dto import WeeklyPlanResponseDTO


def to_weekly_plan_response(
    plan: WeeklyPlan, recipes: list[PlanRecipe]
) -> WeeklyPlanResponseDTO:
    return WeeklyPlanResponseDTO(
        id=plan.id,
        usuario_id=plan.usuario_id,
        fecha_inicio=plan.fecha_inicio,
        recetas=recipes,
    )
