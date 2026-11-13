"""Pruebas de HU12: python -m unittest test_hu12 -v."""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "hu12-test-secret"

import unittest
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.app import app
from src.db.connection import Base, get_db
from src.db.models.comment_model import Comment
from src.db.models.ingrediente_model import Ingredient
from src.db.models.recipe_ingredient_model import RecipeIngredient
from src.db.models.receta_model import Recipe
from src.db.models.step_model import Step
from src.db.models.usuario_model import User


class HU12Tests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

        user = User(email="search@example.com", nombre="Search", password_hash="test")
        self.db.add(user)
        self.db.flush()

        rice = Ingredient(nombre="Arroz", unidad_base="g", origen_animal=False, calorias_por_unidad=1)
        cheese = Ingredient(nombre="Queso", unidad_base="g", origen_animal=True, calorias_por_unidad=4)
        egg = Ingredient(nombre="Huevo", unidad_base="unidad", origen_animal=True, calorias_por_unidad=2)
        onion = Ingredient(nombre="Cebolla", unidad_base="g", origen_animal=False, calorias_por_unidad=0.5)
        self.db.add_all([rice, cheese, egg, onion])
        self.db.flush()

        recipes = [
            Recipe(autor_id=user.id, titulo="Arroz con cebolla", porciones=2, tiempo_min=15, dificultad="facil"),
            Recipe(autor_id=user.id, titulo="Queso y arroz", porciones=2, tiempo_min=25, dificultad="media"),
            Recipe(autor_id=user.id, titulo="Huevo con arroz", porciones=2, tiempo_min=30, dificultad="dificil"),
            Recipe(autor_id=user.id, titulo="Arroz simple", porciones=2, tiempo_min=10, dificultad="facil"),
        ]
        self.db.add_all(recipes)
        self.db.flush()
        self.recipe_ids = {recipe.titulo: recipe.id for recipe in recipes}

        self.db.add_all(
            [
                RecipeIngredient(receta_id=recipes[0].id, ingrediente_id=rice.id, cantidad=Decimal("50")),
                RecipeIngredient(receta_id=recipes[0].id, ingrediente_id=onion.id, cantidad=Decimal("10")),
                RecipeIngredient(receta_id=recipes[1].id, ingrediente_id=rice.id, cantidad=Decimal("80")),
                RecipeIngredient(receta_id=recipes[1].id, ingrediente_id=cheese.id, cantidad=Decimal("30")),
                RecipeIngredient(receta_id=recipes[2].id, ingrediente_id=rice.id, cantidad=Decimal("60")),
                RecipeIngredient(receta_id=recipes[2].id, ingrediente_id=egg.id, cantidad=Decimal("2")),
                RecipeIngredient(receta_id=recipes[3].id, ingrediente_id=rice.id, cantidad=Decimal("100")),
            ]
        )
        self.db.add_all(
            [
                Step(receta_id=recipes[0].id, orden=1, descripcion="Calentar"),
                Step(receta_id=recipes[1].id, orden=1, descripcion="Mezclar"),
                Step(receta_id=recipes[2].id, orden=1, descripcion="Freír"),
                Step(receta_id=recipes[3].id, orden=1, descripcion="Cocinar"),
            ]
        )
        self.db.add_all(
            [
                Comment(usuario_id=user.id, receta_id=recipes[0].id, texto="Muy bien", puntaje=5),
                Comment(usuario_id=user.id, receta_id=recipes[1].id, texto="Bien", puntaje=4),
                Comment(usuario_id=user.id, receta_id=recipes[2].id, texto="Regular", puntaje=2),
            ]
        )
        self.db.commit()

        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()
        self.engine.dispose()

    def test_search_filters_and_sorting(self):
        self.assertEqual(
            [recipe["id"] for recipe in self.client.get("/api/recetas?vegana=true").json()],
            [self.recipe_ids["Arroz con cebolla"], self.recipe_ids["Arroz simple"]],
        )
        self.assertEqual(
            [recipe["id"] for recipe in self.client.get("/api/recetas?dificultad=facil").json()],
            [self.recipe_ids["Arroz con cebolla"], self.recipe_ids["Arroz simple"]],
        )
        self.assertEqual(
            [recipe["id"] for recipe in self.client.get("/api/recetas?tiempo_max=15").json()],
            [self.recipe_ids["Arroz con cebolla"], self.recipe_ids["Arroz simple"]],
        )
        self.assertEqual(
            [recipe["id"] for recipe in self.client.get("/api/recetas?ingrediente=queso").json()],
            [self.recipe_ids["Queso y arroz"]],
        )
        self.assertEqual(
            [recipe["id"] for recipe in self.client.get("/api/recetas?titulo=arroz").json()],
            [self.recipe_ids["Arroz con cebolla"], self.recipe_ids["Queso y arroz"], self.recipe_ids["Huevo con arroz"], self.recipe_ids["Arroz simple"]],
        )
        self.assertEqual(
            [recipe["id"] for recipe in self.client.get("/api/recetas?ordenar_por=puntaje").json()],
            [self.recipe_ids["Arroz con cebolla"], self.recipe_ids["Queso y arroz"], self.recipe_ids["Huevo con arroz"], self.recipe_ids["Arroz simple"]],
        )

    def test_rejects_computed_fields_and_unexpected_params(self):
        self.assertEqual(self.client.get("/api/recetas?es_vegana=true").status_code, 422)
        self.assertEqual(self.client.get("/api/recetas?otra_cosa=true").status_code, 422)


if __name__ == "__main__":
    unittest.main()
