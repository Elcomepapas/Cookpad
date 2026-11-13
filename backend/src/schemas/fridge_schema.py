from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PurchaseItemSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ingrediente_id: int = Field(gt=0)
    nombre_producto: str = Field(min_length=1, max_length=200)
    cantidad: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    precio_total: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    fecha_vencimiento: date | None = None

    @field_validator("nombre_producto")
    @classmethod
    def product_name_must_not_be_blank(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Product name cannot be blank")
        return name


class CreatePurchaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comercio: str = Field(min_length=1, max_length=120)
    fecha_compra: date
    productos: list[PurchaseItemSchema] = Field(min_length=1, max_length=100)

    @field_validator("comercio")
    @classmethod
    def commerce_must_not_be_blank(cls, value: str) -> str:
        commerce = value.strip()
        if not commerce:
            raise ValueError("Commerce name cannot be blank")
        return commerce
