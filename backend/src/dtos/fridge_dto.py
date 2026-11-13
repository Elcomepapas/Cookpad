from datetime import date
from typing import Literal

from pydantic import BaseModel

CategoriaHeladera = Literal[
    "bebidas",
    "aderezos",
    "lacteos",
    "verduras",
    "frutas",
    "carnes_vacunas",
    "carnes_porcinas",
    "carnes_aves",
    "carnes_ovinas",
    "pescados",
    "mariscos",
    "fiambres",
    "otras_carnes",
    "panificados",
    "almacen",
    "congelados",
    "otros",
]


class ReceiptProductPreviewDTO(BaseModel):
    nombre: str
    ingrediente_id: int | None
    categoria: CategoriaHeladera = "otros"
    cantidad: float
    unidad: str
    precio_total: float
    fecha_vencimiento: date | None


class ReceiptPreviewDTO(BaseModel):
    comercio: str
    fecha_compra: date
    productos: list[ReceiptProductPreviewDTO]


class FridgeItemDTO(BaseModel):
    id: int
    ingrediente_id: int
    nombre: str
    categoria: CategoriaHeladera
    cantidad: float
    unidad: str
    precio_total: float
    fecha_vencimiento: date | None
    dias_para_vencer: int | None
    proximo_a_vencer: bool
    vencido: bool


class PurchaseDTO(BaseModel):
    id: int
    comercio: str
    fecha_compra: date
    total: float
    productos: list[FridgeItemDTO]


class FridgeOverviewDTO(BaseModel):
    compras: list[PurchaseDTO]
    total_gastado: float


class MissingRecipeIngredientDTO(BaseModel):
    ingrediente_id: int
    nombre: str
    cantidad: float
    unidad: str


class RecipeShoppingSuggestionDTO(BaseModel):
    receta_id: int
    titulo: str
    ingredientes_disponibles: int
    total_ingredientes: int
    productos_a_comprar: list[MissingRecipeIngredientDTO]


class ShoppingReminderDTO(BaseModel):
    id: int
    nombre: str
