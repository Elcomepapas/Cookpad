from pydantic import BaseModel, Field


class SaveRecipeSchema(BaseModel):
    receta_id: int = Field(gt=0)

    model_config = {"extra": "forbid"}
