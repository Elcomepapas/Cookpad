from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CreateIngredientSchema(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    unidad_base: Literal["g", "ml", "unidad"]
    origen_animal: bool = False
    calorias_por_unidad: Decimal = Field(
        default=Decimal("0"), ge=0, max_digits=10, decimal_places=2
    )

    @field_validator("nombre")
    @classmethod
    def strip_and_validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        return value
