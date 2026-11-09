from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models.ingrediente_model import Ingredient


class IngredientRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_name(self, nombre: str) -> Ingredient | None:
        return self.db.query(Ingredient).filter(Ingredient.nombre == nombre).first()

    def list_all(self) -> list[Ingredient]:
        return self.db.query(Ingredient).order_by(Ingredient.nombre).all()

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
