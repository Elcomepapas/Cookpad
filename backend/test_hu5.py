"""Pruebas aisladas de HU5: python -m unittest test_hu5 -v."""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "hu5-test-secret"

import unittest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.app import app
from src.db.connection import Base, get_db
from src.db.models.usuario_model import User
from src.db.models.receta_model import Recipe
from src.db.models.ingrediente_model import Ingredient
from src.db.models.recipe_ingredient_model import RecipeIngredient
from src.db.models.step_model import Step
from src.middlewares.auth_middleware import get_current_user


class HU5Tests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool,
                                    connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(email="test@example.com", nombre="Test", password_hash="test")
        self.db.add(self.user)
        self.db.flush()
        self.db.add_all([
            Ingredient(id=1, nombre="Arroz", unidad_base="g", origen_animal=False,
                       calorias_por_unidad=1),
            Ingredient(id=2, nombre="Queso", unidad_base="g", origen_animal=True,
                       calorias_por_unidad=2),
        ])
        self.db.flush()
        for recipe_id, ids in [(1, [1]), (2, [1, 2]), (3, [])]:
            self.db.add(Recipe(id=recipe_id, autor_id=self.user.id,
                               titulo=f"Receta {recipe_id}", porciones=2,
                               tiempo_min=10, dificultad="facil"))
            self.db.flush()
            self.db.add_all([RecipeIngredient(receta_id=recipe_id, ingrediente_id=i,
                                              cantidad=Decimal("10")) for i in ids])
            self.db.add(Step(receta_id=recipe_id, orden=1, descripcion="Mezclar"))
        self.db.commit()
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[get_current_user] = lambda: self.user
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()
        self.engine.dispose()

    def test_listing_and_filters(self):
        for suffix, ids in [("", [1, 2, 3]), ("/", [1, 2, 3]),
                            ("?vegana=true", [1, 3]), ("?vegana=false", [2])]:
            response = self.client.get("/api/recetas" + suffix)
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual([r["id"] for r in response.json()], ids)
        self.assertEqual(self.client.get("/api/recetas?vegana=invalid").status_code, 422)

    def test_detail_scaling_and_not_found(self):
        result = self.client.get("/api/recetas/2?porciones=4").json()
        self.assertFalse(result["es_vegana"])
        self.assertEqual(result["ingredientes"][0]["cantidad"], 20)
        self.assertEqual(result["calorias_totales"], 60)
        self.assertEqual(result["calorias_por_porcion"], 15)
        self.assertEqual(self.client.get("/api/recetas/999").status_code, 404)

    def test_create_and_reject_computed_field(self):
        payload = dict(titulo="Nueva", porciones=2, tiempo_min=10, dificultad="facil",
                       ingredientes=[dict(ingrediente_id=1, cantidad=10)],
                       pasos=[dict(orden=1, descripcion="Cocinar")])
        response = self.client.post("/api/recetas/", json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        self.assertTrue(response.json()["es_vegana"])
        payload["es_vegana"] = False
        self.assertEqual(self.client.post("/api/recetas/", json=payload).status_code, 422)

    def test_changes_to_ingredients_are_reflected(self):
        self.assertTrue(self.client.get("/api/recetas/1").json()["es_vegana"])
        self.db.get(Ingredient, 1).origen_animal = True
        self.db.commit()
        self.assertFalse(self.client.get("/api/recetas/1").json()["es_vegana"])
        self.assertEqual([r["id"] for r in
                         self.client.get("/api/recetas?vegana=true").json()], [3])

    def test_batch_loading_and_no_persisted_field(self):
        queries = []
        def record(conn, cursor, statement, parameters, context, executemany):
            if statement.lstrip().upper().startswith("SELECT"):
                queries.append(statement)
        event.listen(self.engine, "before_cursor_execute", record)
        response = self.client.get("/api/recetas")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(queries), 4)
        self.assertNotIn("es_vegana", Recipe.__table__.columns)

    def test_empty_list_and_existing_routes(self):
        self.db.query(RecipeIngredient).delete()
        self.db.query(Step).delete()
        self.db.query(Recipe).delete()
        self.db.commit()
        self.assertEqual(self.client.get("/api/recetas").json(), [])
        self.assertEqual(self.client.get("/health").json(), {"status": "ok"})
        paths = app.openapi()["paths"]
        self.assertIn("/api/recetas/{recipe_id}", paths)
        self.assertIn("/api/recetas/", paths)
        self.assertIn("vegana", str(paths["/api/recetas"]["get"]["parameters"]))


if __name__ == "__main__":
    unittest.main()
