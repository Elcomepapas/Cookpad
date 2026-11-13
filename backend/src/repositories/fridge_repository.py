from datetime import date
from decimal import Decimal

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from src.db.models.ingrediente_model import Ingredient
from src.db.models.purchase_model import FridgeItem, Purchase, ShoppingReminder
from src.db.models.recipe_ingredient_model import RecipeIngredient
from src.db.models.receta_model import Recipe
from src.db.models.saved_recipe_model import SavedRecipe


class FridgeRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_ingredient(self, ingredient_id: int) -> Ingredient | None:
        return self.db.get(Ingredient, ingredient_id)

    def find_ingredient_by_name(self, name: str) -> Ingredient | None:
        return self.db.scalars(
            select(Ingredient).where(func.lower(Ingredient.nombre) == name.lower())
        ).first()

    def create_purchase(
        self,
        user_id: int,
        commerce: str,
        purchase_date: date,
        products: list[dict[str, int | Decimal | date | None | str]],
    ) -> Purchase:
        purchase = Purchase(
            usuario_id=user_id,
            comercio=commerce.strip(),
            fecha_compra=purchase_date,
        )
        purchase.productos = [FridgeItem(**product) for product in products]
        acquired_names = {
            str(product["nombre_producto"]).strip().casefold()
            for product in products
        }
        ingredient_ids = {int(product["ingrediente_id"]) for product in products}
        if ingredient_ids:
            catalog_names = self.db.scalars(
                select(Ingredient.nombre).where(Ingredient.id.in_(ingredient_ids))
            ).all()
            acquired_names.update(name.strip().casefold() for name in catalog_names)

        try:
            self.db.add(purchase)
            self.db.flush()
            if acquired_names:
                self.db.execute(
                    delete(ShoppingReminder).where(
                        ShoppingReminder.usuario_id == user_id,
                        ShoppingReminder.nombre_normalizado.in_(acquired_names),
                    )
                )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(purchase)
        return purchase

    def list_purchases(self, user_id: int) -> list[tuple[Purchase, list[FridgeItem]]]:
        purchases = (
            self.db.scalars(
                select(Purchase)
                .where(Purchase.usuario_id == user_id)
                .order_by(Purchase.fecha_compra.desc(), Purchase.id.desc())
            )
            .all()
        )
        if not purchases:
            return []
        items = self.db.scalars(
            select(FridgeItem)
            .where(FridgeItem.compra_id.in_([purchase.id for purchase in purchases]))
            .order_by(FridgeItem.id)
        ).all()
        items_by_purchase: dict[int, list[FridgeItem]] = {
            purchase.id: [] for purchase in purchases
        }
        for item in items:
            items_by_purchase[item.compra_id].append(item)
        return [(purchase, items_by_purchase[purchase.id]) for purchase in purchases]

    def ingredients_by_ids(self, ingredient_ids: set[int]) -> dict[int, Ingredient]:
        if not ingredient_ids:
            return {}
        return {
            ingredient.id: ingredient
            for ingredient in self.db.scalars(
                select(Ingredient).where(Ingredient.id.in_(ingredient_ids))
            ).all()
        }

    def saved_recipe_ingredients(
        self, user_id: int
    ) -> list[tuple[Recipe, list[tuple[RecipeIngredient, Ingredient]]]]:
        rows = self.db.execute(
            select(Recipe, RecipeIngredient, Ingredient)
            .join(SavedRecipe, SavedRecipe.receta_id == Recipe.id)
            .join(RecipeIngredient, RecipeIngredient.receta_id == Recipe.id)
            .join(Ingredient, Ingredient.id == RecipeIngredient.ingrediente_id)
            .where(SavedRecipe.usuario_id == user_id)
            .order_by(SavedRecipe.fecha.desc(), Recipe.id, Ingredient.id)
        ).all()
        grouped: dict[int, tuple[Recipe, list[tuple[RecipeIngredient, Ingredient]]]] = {}
        for recipe, recipe_ingredient, ingredient in rows:
            grouped.setdefault(recipe.id, (recipe, []))[1].append(
                (recipe_ingredient, ingredient)
            )
        return list(grouped.values())

    def available_ingredient_ids(self, user_id: int, today: date) -> set[int]:
        return set(
            self.db.scalars(
                select(FridgeItem.ingrediente_id)
                .join(Purchase, Purchase.id == FridgeItem.compra_id)
                .where(
                    Purchase.usuario_id == user_id,
                    (FridgeItem.fecha_vencimiento.is_(None))
                    | (FridgeItem.fecha_vencimiento >= today),
                )
                .distinct()
            ).all()
        )

    def list_reminders(self, user_id: int) -> list[ShoppingReminder]:
        return list(
            self.db.scalars(
                select(ShoppingReminder)
                .where(ShoppingReminder.usuario_id == user_id)
                .order_by(ShoppingReminder.id)
            ).all()
        )

    def add_reminders(self, user_id: int, names: list[str]) -> list[ShoppingReminder]:
        existing_names = set(
            self.db.scalars(
                select(ShoppingReminder.nombre_normalizado).where(
                    ShoppingReminder.usuario_id == user_id
                )
            ).all()
        )
        new_reminders = []
        seen_names = set(existing_names)
        for name in names:
            normalized = name.casefold()
            if normalized in seen_names:
                continue
            seen_names.add(normalized)
            new_reminders.append(
                ShoppingReminder(
                    usuario_id=user_id,
                    nombre=name,
                    nombre_normalizado=normalized,
                )
            )
        self.db.add_all(new_reminders)
        self.db.commit()
        return self.list_reminders(user_id)

    def delete_reminder(self, user_id: int, reminder_id: int) -> bool:
        reminder = self.db.scalar(
            select(ShoppingReminder).where(
                ShoppingReminder.id == reminder_id,
                ShoppingReminder.usuario_id == user_id,
            )
        )
        if reminder is None:
            return False
        self.db.delete(reminder)
        self.db.commit()
        return True

    def update_item_category(
        self, user_id: int, item_id: int, category: str
    ) -> FridgeItem | None:
        item = self.db.scalar(
            select(FridgeItem)
            .join(Purchase, Purchase.id == FridgeItem.compra_id)
            .where(
                FridgeItem.id == item_id,
                Purchase.usuario_id == user_id,
            )
        )
        if item is None:
            return None
        item.categoria = category
        self.db.commit()
        self.db.refresh(item)
        return item
