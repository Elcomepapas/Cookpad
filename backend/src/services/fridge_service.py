from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from src.dtos.fridge_dto import (
    FridgeItemDTO,
    FridgeOverviewDTO,
    MissingRecipeIngredientDTO,
    PurchaseDTO,
    ReceiptPreviewDTO,
    RecipeShoppingSuggestionDTO,
)
from src.repositories.fridge_repository import FridgeRepository
from src.schemas.fridge_schema import CreatePurchaseSchema
from src.utils.errors import BadRequestError, NotFoundError
from src.utils.receipt_pdf import (
    MAX_RECEIPT_BYTES,
    extract_receipt_text,
    parse_receipt_text,
)


class FridgeService:
    def __init__(self, db: Session):
        self.repo = FridgeRepository(db)

    def preview_receipt(self, content: bytes) -> ReceiptPreviewDTO:
        if not content or len(content) > MAX_RECEIPT_BYTES:
            raise BadRequestError("Receipt PDF must be between 1 byte and 5 MB")
        preview = parse_receipt_text(extract_receipt_text(content))
        for product in preview.productos:
            ingredient = self.repo.find_ingredient_by_name(product.nombre)
            if ingredient is not None and ingredient.unidad_base == product.unidad:
                product.ingrediente_id = ingredient.id
        return preview

    def create_purchase(self, user_id: int, payload: CreatePurchaseSchema) -> PurchaseDTO:
        products: list[dict] = []
        for item in payload.productos:
            ingredient = self.repo.find_ingredient(item.ingrediente_id)
            if ingredient is None:
                raise NotFoundError(f"Ingredient {item.ingrediente_id} not found")
            products.append(
                {
                    "ingrediente_id": ingredient.id,
                    "nombre_producto": item.nombre_producto,
                    "cantidad": item.cantidad,
                    "precio_total": item.precio_total,
                    "fecha_vencimiento": item.fecha_vencimiento,
                }
            )

        purchase = self.repo.create_purchase(
            user_id,
            payload.comercio,
            payload.fecha_compra,
            products,
        )
        ingredients = self.repo.ingredients_by_ids(
            {product["ingrediente_id"] for product in products}
        )
        today = date.today()
        items = [
            self._item_dto(item, ingredients[item.ingrediente_id], today)
            for item in purchase.productos
        ]
        return PurchaseDTO(
            id=purchase.id,
            comercio=purchase.comercio,
            fecha_compra=purchase.fecha_compra,
            total=sum((item.precio_total for item in purchase.productos), Decimal("0")),
            productos=items,
        )

    def overview(self, user_id: int) -> FridgeOverviewDTO:
        purchases = self.repo.list_purchases(user_id)
        ingredient_ids = {
            item.ingrediente_id for _, items in purchases for item in items
        }
        ingredients = self.repo.ingredients_by_ids(ingredient_ids)
        today = date.today()
        purchase_dtos = []
        grand_total = Decimal("0")
        for purchase, items in purchases:
            item_dtos = [
                self._item_dto(item, ingredients[item.ingrediente_id], today)
                for item in items
            ]
            total = sum((item.precio_total for item in items), Decimal("0"))
            grand_total += total
            purchase_dtos.append(
                PurchaseDTO(
                    id=purchase.id,
                    comercio=purchase.comercio,
                    fecha_compra=purchase.fecha_compra,
                    total=total,
                    productos=item_dtos,
                )
            )
        return FridgeOverviewDTO(compras=purchase_dtos, total_gastado=grand_total)

    def suggestions(self, user_id: int) -> list[RecipeShoppingSuggestionDTO]:
        available = self.repo.available_ingredient_ids(user_id, date.today())
        suggestions = []
        for recipe, ingredients in self.repo.saved_recipe_ingredients(user_id):
            in_fridge = [
                (recipe_ingredient, ingredient)
                for recipe_ingredient, ingredient in ingredients
                if ingredient.id in available
            ]
            missing = [
                (recipe_ingredient, ingredient)
                for recipe_ingredient, ingredient in ingredients
                if ingredient.id not in available
            ]
            if not in_fridge or not missing:
                continue
            suggestions.append(
                RecipeShoppingSuggestionDTO(
                    receta_id=recipe.id,
                    titulo=recipe.titulo,
                    ingredientes_disponibles=len(in_fridge),
                    total_ingredientes=len(ingredients),
                    productos_a_comprar=[
                        MissingRecipeIngredientDTO(
                            ingrediente_id=ingredient.id,
                            nombre=ingredient.nombre,
                            cantidad=recipe_ingredient.cantidad,
                            unidad=ingredient.unidad_base,
                        )
                        for recipe_ingredient, ingredient in missing
                    ],
                )
            )
        return suggestions

    @staticmethod
    def _item_dto(item, ingredient, today: date) -> FridgeItemDTO:
        days = (
            (item.fecha_vencimiento - today).days
            if item.fecha_vencimiento is not None
            else None
        )
        return FridgeItemDTO(
            id=item.id,
            ingrediente_id=ingredient.id,
            nombre=item.nombre_producto,
            cantidad=item.cantidad,
            unidad=ingredient.unidad_base,
            precio_total=item.precio_total,
            fecha_vencimiento=item.fecha_vencimiento,
            dias_para_vencer=days,
            proximo_a_vencer=days is not None and 0 <= days <= 7,
            vencido=days is not None and days < 0,
        )
