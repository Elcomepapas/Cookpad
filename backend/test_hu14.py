"""Pruebas de Mi heladera: python -m unittest test_hu14 -v."""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "hu14-test-secret"

import unittest
from io import BytesIO
from datetime import date, timedelta

from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.app import app
from src.db.connection import Base, get_db
from src.db.models.ingrediente_model import Ingredient
from src.db.models.recipe_ingredient_model import RecipeIngredient
from src.db.models.receta_model import Recipe
from src.db.models.saved_recipe_model import SavedRecipe
from src.db.models.usuario_model import User
from src.middlewares.auth_middleware import get_current_user
from src.utils.errors import BadRequestError
from src.utils.receipt_pdf import extract_receipt_text, parse_receipt_text


def fixed_receipt_pdf(text: str) -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = writer._add_object(
        DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            }
        )
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font}),
        }
    )
    lines = text.splitlines()
    commands = ["BT", "/F1 9 Tf", "50 750 Td"]
    for index, line in enumerate(lines):
        if index:
            commands.append("0 -16 Td")
        commands.append(f"({line}) Tj")
    commands.append("ET")
    content = DecodedStreamObject()
    content.set_data("\n".join(commands).encode("ascii"))
    page[NameObject("/Contents")] = writer._add_object(content)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


class FridgeTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(
            email="fridge@example.com", nombre="Fridge", password_hash="test"
        )
        another_user = User(
            email="other@example.com", nombre="Other", password_hash="test"
        )
        self.db.add_all([self.user, another_user])
        self.db.flush()
        self.other_user = another_user

        rice = Ingredient(
            nombre="Arroz", unidad_base="g", origen_animal=False, calorias_por_unidad=1
        )
        onion = Ingredient(
            nombre="Cebolla", unidad_base="unidad", origen_animal=False, calorias_por_unidad=1
        )
        chicken = Ingredient(
            nombre="Pollo", unidad_base="g", origen_animal=True, calorias_por_unidad=1
        )
        self.db.add_all([rice, onion, chicken])
        self.db.flush()
        self.rice, self.onion, self.chicken = rice, onion, chicken

        saved_recipe = Recipe(
            autor_id=self.user.id,
            titulo="Arroz con cebolla",
            porciones=2,
            tiempo_min=20,
            dificultad="facil",
        )
        complete_recipe = Recipe(
            autor_id=self.user.id,
            titulo="Arroz simple",
            porciones=2,
            tiempo_min=10,
            dificultad="facil",
        )
        unsaved_recipe = Recipe(
            autor_id=self.user.id,
            titulo="Pollo con arroz no guardado",
            porciones=2,
            tiempo_min=30,
            dificultad="media",
        )
        self.db.add_all([saved_recipe, complete_recipe, unsaved_recipe])
        self.db.flush()
        self.saved_recipe = saved_recipe
        self.db.add_all(
            [
                RecipeIngredient(
                    receta_id=saved_recipe.id, ingrediente_id=rice.id, cantidad=100
                ),
                RecipeIngredient(
                    receta_id=saved_recipe.id, ingrediente_id=onion.id, cantidad=1
                ),
                RecipeIngredient(
                    receta_id=complete_recipe.id, ingrediente_id=rice.id, cantidad=50
                ),
                RecipeIngredient(
                    receta_id=unsaved_recipe.id, ingrediente_id=rice.id, cantidad=50
                ),
                RecipeIngredient(
                    receta_id=unsaved_recipe.id, ingrediente_id=chicken.id, cantidad=100
                ),
                SavedRecipe(usuario_id=self.user.id, receta_id=saved_recipe.id),
                SavedRecipe(usuario_id=self.user.id, receta_id=complete_recipe.id),
            ]
        )
        self.db.commit()

        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[get_current_user] = lambda: self.user
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()
        self.engine.dispose()

    def add_purchase(self, commerce, rice_price, onion_expiry=None):
        return self.client.post(
            "/api/heladera/compras",
            json={
                "comercio": commerce,
                "fecha_compra": date.today().isoformat(),
                "productos": [
                    {
                        "ingrediente_id": self.rice.id,
                        "nombre_producto": "Arroz",
                        "cantidad": 500,
                        "precio_total": rice_price,
                        "fecha_vencimiento": (date.today() + timedelta(days=30)).isoformat(),
                    },
                    *(
                        [
                            {
                                "ingrediente_id": self.onion.id,
                                "nombre_producto": "Cebolla",
                                "cantidad": 2,
                                "precio_total": 700,
                                "fecha_vencimiento": onion_expiry,
                            }
                        ]
                        if onion_expiry is not None
                        else []
                    ),
                ],
            },
        )

    def test_purchases_remain_separate_and_global_total_is_summed(self):
        first = self.add_purchase("Supermercado", "1800")
        second = self.add_purchase("Verdulería", "900")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertEqual(first.json()["total"], 1800)
        self.assertEqual(first.json()["productos"][0]["nombre"], "Arroz")

        overview = self.client.get("/api/heladera")
        self.assertEqual(overview.status_code, 200)
        self.assertEqual(overview.json()["total_gastado"], 2700)
        self.assertEqual(len(overview.json()["compras"]), 2)
        self.assertEqual(
            {purchase["comercio"] for purchase in overview.json()["compras"]},
            {"Supermercado", "Verdulería"},
        )

    def test_expiry_alert_and_saved_recipe_suggestions(self):
        expiry = (date.today() + timedelta(days=5)).isoformat()
        self.client.post(
            "/api/heladera/compras",
            json={
                "comercio": "Supermercado",
                "fecha_compra": date.today().isoformat(),
                "productos": [
                    {
                        "ingrediente_id": self.rice.id,
                        "nombre_producto": "Arroz",
                        "cantidad": 500,
                        "precio_total": 1800,
                        "fecha_vencimiento": expiry,
                    }
                ],
            },
        )

        overview = self.client.get("/api/heladera").json()
        items = [item for purchase in overview["compras"] for item in purchase["productos"]]
        rice = next(item for item in items if item["nombre"] == "Arroz")
        self.assertTrue(rice["proximo_a_vencer"])
        self.assertEqual(rice["dias_para_vencer"], 5)

        suggestions = self.client.get("/api/heladera/sugerencias").json()
        self.assertEqual([item["titulo"] for item in suggestions], ["Arroz con cebolla"])
        self.assertEqual(
            [item["nombre"] for item in suggestions[0]["productos_a_comprar"]],
            ["Cebolla"],
        )

    def test_expired_products_do_not_count_as_available(self):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        self.client.post(
            "/api/heladera/compras",
            json={
                "comercio": "Almacén",
                "fecha_compra": date.today().isoformat(),
                "productos": [
                    {
                        "ingrediente_id": self.rice.id,
                        "nombre_producto": "Arroz",
                        "cantidad": 100,
                        "precio_total": 100,
                        "fecha_vencimiento": yesterday,
                    }
                ],
            },
        )
        item = self.client.get("/api/heladera").json()["compras"][0]["productos"][0]
        self.assertTrue(item["vencido"])
        self.assertEqual(self.client.get("/api/heladera/sugerencias").json(), [])

    def test_receipt_preview_maps_catalog_items_and_accepts_missing_expiry(self):
        text = "\n".join(
            [
                "COOKPAD_RECIBO|1",
                "COMERCIO|Supermercado",
                f"FECHA|{date.today().isoformat()}",
                "PRODUCTO|Arroz|500|g|1800.00|",
                "PRODUCTO|Producto desconocido|1|unidad|20.00|",
            ]
        )
        content = fixed_receipt_pdf(text)
        response = self.client.post(
            "/api/heladera/recibos/preview",
            files={"file": ("recibo.pdf", content, "application/pdf")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["productos"][0]["ingrediente_id"], self.rice.id)
        self.assertIsNone(response.json()["productos"][0]["fecha_vencimiento"])
        self.assertIsNone(response.json()["productos"][1]["ingrediente_id"])

    def test_receipt_upload_rejects_non_pdf_content(self):
        response = self.client.post(
            "/api/heladera/recibos/preview",
            files={"file": ("recibo.pdf", b"not a pdf", "application/pdf")},
        )
        self.assertEqual(response.status_code, 400)

    def test_receipt_text_parser_rejects_malformed_rows(self):
        with self.assertRaises(BadRequestError):
            parse_receipt_text(
                "COOKPAD_RECIBO|1\nCOMERCIO|Tienda\nFECHA|2026-01-01\nPRODUCTO|Mala fila"
            )

    def test_inventory_is_private_to_authenticated_user(self):
        self.add_purchase("Solo mío", "100")
        app.dependency_overrides[get_current_user] = lambda: self.other_user
        self.assertEqual(self.client.get("/api/heladera").json()["compras"], [])


if __name__ == "__main__":
    unittest.main()
