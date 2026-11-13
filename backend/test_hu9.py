"""Pruebas de HU9: python -m unittest test_hu9 -v."""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "hu9-test-secret"

import unittest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.app import app
from src.db.connection import Base, get_db
from src.db.models.receta_model import Recipe
from src.db.models.usuario_model import User
from src.db.models.weekly_plan_model import WeeklyPlan
from src.db.models.plan_recipe_model import PlanRecipe
from src.middlewares.auth_middleware import get_current_user


class HU9Tests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(
            email="plan@example.com", nombre="Plan", password_hash="test"
        )
        self.other_user = User(
            email="other@example.com", nombre="Other", password_hash="test"
        )
        self.db.add_all([self.user, self.other_user])
        self.db.flush()
        self.recipe = Recipe(
            autor_id=self.user.id,
            titulo="Receta de prueba",
            porciones=2,
            tiempo_min=20,
            dificultad="facil",
        )
        self.db.add(self.recipe)
        self.db.commit()

        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[get_current_user] = lambda: self.user
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()
        self.engine.dispose()

    def test_create_plan_requires_monday_and_prevents_duplicates(self):
        invalid = self.client.post("/api/planes", json={"fecha_inicio": "2026-11-13"})
        self.assertEqual(invalid.status_code, 422)

        payload = {"fecha_inicio": "2026-11-09"}
        response = self.client.post("/api/planes", json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["fecha_inicio"], "2026-11-09")
        self.assertEqual(response.json()["recetas"], [])
        self.assertEqual(self.client.post("/api/planes", json=payload).status_code, 409)

    def test_add_and_remove_plan_recipe(self):
        plan = WeeklyPlan(usuario_id=self.user.id, fecha_inicio=date(2026, 11, 9))
        self.db.add(plan)
        self.db.commit()

        payload = {
            "receta_id": self.recipe.id,
            "dia_semana": 1,
            "comida": "almuerzo",
            "porciones": 4,
        }
        response = self.client.post(f"/api/planes/{plan.id}/recetas", json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        entry = response.json()["recetas"][0]
        self.assertEqual(entry["porciones"], 4)
        self.assertEqual(entry["comida"], "almuerzo")

        duplicate = self.client.post(f"/api/planes/{plan.id}/recetas", json=payload)
        self.assertEqual(duplicate.status_code, 409)
        invalid_day = {**payload, "dia_semana": 8}
        self.assertEqual(
            self.client.post(f"/api/planes/{plan.id}/recetas", json=invalid_day).status_code,
            422,
        )
        invalid_meal = {**payload, "comida": "brunch"}
        self.assertEqual(
            self.client.post(f"/api/planes/{plan.id}/recetas", json=invalid_meal).status_code,
            422,
        )

        removed = self.client.delete(
            f"/api/planes/{plan.id}/recetas/{entry['id']}"
        )
        self.assertEqual(removed.status_code, 200, removed.text)
        self.assertEqual(removed.json()["recetas"], [])
        self.assertIsNone(self.db.get(PlanRecipe, entry["id"]))

    def test_recipe_must_exist_and_plan_is_private(self):
        plan = WeeklyPlan(usuario_id=self.user.id, fecha_inicio=date(2026, 11, 9))
        foreign_plan = WeeklyPlan(
            usuario_id=self.other_user.id, fecha_inicio=date(2026, 11, 9)
        )
        self.db.add_all([plan, foreign_plan])
        self.db.commit()

        missing_recipe = self.client.post(
            f"/api/planes/{plan.id}/recetas",
            json={
                "receta_id": 999,
                "dia_semana": 1,
                "comida": "cena",
                "porciones": 2,
            },
        )
        self.assertEqual(missing_recipe.status_code, 404)
        self.assertEqual(self.client.get(f"/api/planes/{foreign_plan.id}").status_code, 403)
        self.assertEqual(self.client.get("/api/planes/999").status_code, 404)


if __name__ == "__main__":
    unittest.main()
