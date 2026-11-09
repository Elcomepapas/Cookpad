from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CreateRecipeIngredientDTO(BaseModel):
    ingrediente_id: int
    cantidad: Decimal


class CreateStepDTO(BaseModel):
    orden: int
    descripcion: str


class CreateRecipeDTO(BaseModel):
    titulo: str
    porciones: int
    tiempo_min: int
    dificultad: str
    ingredientes: list[CreateRecipeIngredientDTO]
    pasos: list[CreateStepDTO]


class RecipeIngredientResponseDTO(BaseModel):
    ingrediente_id: int
    nombre: str
    unidad_base: str
    cantidad: float


class StepResponseDTO(BaseModel):
    id: int
    orden: int
    descripcion: str


class RecipeResponseDTO(BaseModel):
    id: int
    autor_id: int
    titulo: str
    porciones: int
    tiempo_min: int
    dificultad: str
    fecha_publicacion: datetime
    ingredientes: list[RecipeIngredientResponseDTO] = Field(default_factory=list)
    pasos: list[StepResponseDTO] = Field(default_factory=list)

    model_config = {"from_attributes": True}
