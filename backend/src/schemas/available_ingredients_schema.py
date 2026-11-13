from pydantic import BaseModel, Field, field_validator


class AvailableIngredientsSchema(BaseModel):
    ingredientes_ids: list[int] = Field(max_length=500)

    model_config = {"extra": "forbid"}

    @field_validator("ingredientes_ids")
    @classmethod
    def validate_ingredient_ids(cls, value: list[int]) -> list[int]:
        if any(ingredient_id <= 0 for ingredient_id in value):
            raise ValueError("Los IDs de ingredientes deben ser positivos")
        return value
