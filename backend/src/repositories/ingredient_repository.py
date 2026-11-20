from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models.ingrediente_model import Ingredient
from src.db.models.recipe_ingredient_model import RecipeIngredient


class IngredientRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_name(self, nombre: str) -> Ingredient | None:
        return self.db.query(Ingredient).filter(Ingredient.nombre == nombre).first()

    def list_all(self) -> list[Ingredient]:
        return self.db.query(Ingredient).order_by(Ingredient.nombre).all()

    def list_most_used(self) -> list[tuple[Ingredient, int]]:
        usage_count = func.count(RecipeIngredient.receta_id)
        return (
            self.db.query(Ingredient, usage_count)
            .join(RecipeIngredient, RecipeIngredient.ingrediente_id == Ingredient.id)
            .group_by(Ingredient.id)
            .order_by(usage_count.desc(), Ingredient.nombre, Ingredient.id)
            .limit(10)
            .all()
        )

    def create(
        self,
        nombre: str,
        unidad_base: str,
        calorias_por_unidad: Decimal,
        origen_animal: bool,
    ) -> Ingredient:
        ingredient = Ingredient(
            nombre=nombre,
            unidad_base=unidad_base,
            origen_animal=origen_animal,
            calorias_por_unidad=calorias_por_unidad,
        )
        self.db.add(ingredient)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(ingredient)
        return ingredient
