"""Pruebas de HU10: python -m unittest test_hu10 -v."""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "hu10-test-secret"

import unittest
from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.app import app
from src.db.connection import Base, get_db
from src.db.models.ingrediente_model import Ingredient
from src.db.models.plan_recipe_model import PlanRecipe
from src.db.models.receta_model import Recipe
from src.db.models.recipe_ingredient_model import RecipeIngredient
from src.db.models.usuario_model import User
from src.db.models.weekly_plan_model import WeeklyPlan
from src.middlewares.auth_middleware import get_current_user


class HU10Tests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(
            email="shopping@example.com", nombre="Shopping", password_hash="test"
        )
        self.other_user = User(
            email="other-shopping@example.com", nombre="Other", password_hash="test"
        )
        self.db.add_all([self.user, self.other_user])
        self.db.flush()

        oats = Ingredient(
            nombre="Avena", unidad_base="g", calorias_por_unidad=Decimal("3.89")
        )
        rice = Ingredient(
            nombre="Arroz", unidad_base="g", calorias_por_unidad=Decimal("3.60")
        )
        carrot = Ingredient(
            nombre="Zanahoria", unidad_base="g", calorias_por_unidad=Decimal("0.41")
        )
        self.db.add_all([oats, rice, carrot])
        self.db.flush()

        recipe_one = Recipe(
            autor_id=self.user.id,
            titulo="Receta uno",
            porciones=2,
            tiempo_min=15,
            dificultad="facil",
        )
        recipe_two = Recipe(
            autor_id=self.user.id,
            titulo="Receta dos",
            porciones=3,
            tiempo_min=20,
            dificultad="media",
        )
        self.db.add_all([recipe_one, recipe_two])
        self.db.flush()
        self.db.add_all(
            [
                RecipeIngredient(
                    receta_id=recipe_one.id,
                    ingrediente_id=rice.id,
                    cantidad=Decimal("100"),
                ),
                RecipeIngredient(
                    receta_id=recipe_one.id,
                    ingrediente_id=oats.id,
                    cantidad=Decimal("30"),
                ),
                RecipeIngredient(
                    receta_id=recipe_two.id,
                    ingrediente_id=rice.id,
                    cantidad=Decimal("150"),
                ),
                RecipeIngredient(
                    receta_id=recipe_two.id,
                    ingrediente_id=carrot.id,
                    cantidad=Decimal("50"),
                ),
            ]
        )

        self.plan = WeeklyPlan(usuario_id=self.user.id, fecha_inicio=date(2026, 11, 9))
        self.foreign_plan = WeeklyPlan(
            usuario_id=self.other_user.id, fecha_inicio=date(2026, 11, 9)
        )
        self.db.add_all([self.plan, self.foreign_plan])
        self.db.flush()
        self.db.add_all(
            [
                PlanRecipe(
                    plan_id=self.plan.id,
                    receta_id=recipe_one.id,
                    dia_semana=1,
                    comida="almuerzo",
                    porciones=4,
                ),
                PlanRecipe(
                    plan_id=self.plan.id,
                    receta_id=recipe_two.id,
                    dia_semana=2,
                    comida="cena",
                    porciones=6,
                ),
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

    def test_scales_combines_and_sorts_shopping_list(self):
        response = self.client.get(
            f"/api/planes/{self.plan.id}/lista-compras"
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(
            response.json(),
            [
                {
                    "ingrediente_id": self.db.query(Ingredient.id)
                    .filter(Ingredient.nombre == "Arroz")
                    .scalar(),
                    "nombre": "Arroz",
                    "unidad_base": "g",
                    "cantidad": 500.0,
                },
                {
                    "ingrediente_id": self.db.query(Ingredient.id)
                    .filter(Ingredient.nombre == "Avena")
                    .scalar(),
                    "nombre": "Avena",
                    "unidad_base": "g",
                    "cantidad": 60.0,
                },
                {
                    "ingrediente_id": self.db.query(Ingredient.id)
                    .filter(Ingredient.nombre == "Zanahoria")
                    .scalar(),
                    "nombre": "Zanahoria",
                    "unidad_base": "g",
                    "cantidad": 100.0,
                },
            ],
        )

    def test_empty_list_and_plan_ownership(self):
        self.db.query(PlanRecipe).filter(
            PlanRecipe.plan_id == self.plan.id
        ).delete()
        self.db.commit()
        self.assertEqual(
            self.client.get(f"/api/planes/{self.plan.id}/lista-compras").json(),
            [],
        )
        self.assertEqual(
            self.client.get(
                f"/api/planes/{self.foreign_plan.id}/lista-compras"
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.get("/api/planes/999/lista-compras").status_code,
            404,
        )


if __name__ == "__main__":
    unittest.main()
