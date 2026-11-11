from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class CreateRecipeIngredientSchema(BaseModel):
    ingrediente_id: int = Field(gt=0)
    cantidad: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class CreateStepSchema(BaseModel):
    orden: int = Field(ge=1)
    descripcion: str = Field(min_length=1)

    @field_validator("descripcion")
    @classmethod
    def strip_and_validate_description(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("La descripción del paso no puede estar vacía")
        return value


class CreateRecipeSchema(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def reject_computed_fields(cls, value):
        if isinstance(value, dict) and "es_vegana" in value:
            raise ValueError("es_vegana se calcula automáticamente y no se recibe")
        return value

    titulo: str = Field(min_length=1, max_length=200)
    porciones: int = Field(gt=0)
    tiempo_min: int = Field(gt=0)
    dificultad: Literal["facil", "media", "dificil"]
    ingredientes: list[CreateRecipeIngredientSchema] = Field(min_length=1)
    pasos: list[CreateStepSchema] = Field(min_length=1)

    @field_validator("titulo")
    @classmethod
    def strip_and_validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El título no puede estar vacío")
        return value

    @model_validator(mode="after")
    def validate_recipe_children(self):
        ingredient_ids = [item.ingrediente_id for item in self.ingredientes]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValueError("No se puede repetir un ingrediente en la receta")

        orders = sorted(step.orden for step in self.pasos)
        expected_orders = list(range(1, len(self.pasos) + 1))
        if orders != expected_orders:
            raise ValueError("Los pasos deben tener órdenes consecutivos desde 1")
        return self
