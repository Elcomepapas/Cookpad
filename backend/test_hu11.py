"""Pruebas de HU11: python -m unittest test_hu11 -v."""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "hu11-test-secret"

import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.app import app
from src.db.connection import Base, get_db
from src.db.models.ingrediente_model import Ingredient
from src.db.models.receta_model import Recipe
from src.db.models.recipe_ingredient_model import RecipeIngredient
from src.db.models.usuario_model import User


class HU11Tests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

        user = User(
            email="ingredients@example.com",
            nombre="Ingredients",
            password_hash="test",
        )
        self.db.add(user)
        self.db.flush()

        rice = Ingredient(
            nombre="Arroz", unidad_base="g", calorias_por_unidad=1
        )
        beans = Ingredient(
            nombre="Porotos", unidad_base="g", calorias_por_unidad=1
        )
        egg = Ingredient(
            nombre="Huevo", unidad_base="unidad", calorias_por_unidad=1
        )
        onion = Ingredient(
            nombre="Cebolla", unidad_base="g", calorias_por_unidad=1
        )
        self.db.add_all([rice, beans, egg, onion])
        self.db.flush()

        recipes = [
            Recipe(
                autor_id=user.id,
                titulo="Arroz",
                porciones=2,
                tiempo_min=10,
                dificultad="facil",
            ),
            Recipe(
                autor_id=user.id,
                titulo="Arroz con porotos",
                porciones=2,
                tiempo_min=20,
                dificultad="facil",
            ),
            Recipe(
                autor_id=user.id,
                titulo="Huevo",
                porciones=1,
                tiempo_min=5,
                dificultad="facil",
            ),
            Recipe(
                autor_id=user.id,
                titulo="Arroz con cebolla",
                porciones=2,
                tiempo_min=15,
                dificultad="facil",
            ),
            Recipe(
                autor_id=user.id,
                titulo="Sin ingredientes",
                porciones=1,
                tiempo_min=1,
                dificultad="facil",
            ),
        ]
        self.db.add_all(recipes)
        self.db.flush()
        self.recipe_ids = {recipe.titulo: recipe.id for recipe in recipes}
        self.db.add_all(
            [
                RecipeIngredient(
                    receta_id=recipes[0].id,
                    ingrediente_id=rice.id,
                    cantidad=100,
                ),
                RecipeIngredient(
                    receta_id=recipes[1].id,
                    ingrediente_id=rice.id,
                    cantidad=100,
                ),
                RecipeIngredient(
                    receta_id=recipes[1].id,
                    ingrediente_id=beans.id,
                    cantidad=50,
                ),
                RecipeIngredient(
                    receta_id=recipes[2].id,
                    ingrediente_id=egg.id,
                    cantidad=2,
                ),
                RecipeIngredient(
                    receta_id=recipes[3].id,
                    ingrediente_id=rice.id,
                    cantidad=100,
                ),
                RecipeIngredient(
                    receta_id=recipes[3].id,
                    ingrediente_id=onion.id,
                    cantidad=25,
                ),
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

    def test_returns_recipes_using_only_supplied_ingredients(self):
        rice_id = (
            self.db.query(Ingredient.id)
            .filter(Ingredient.nombre == "Arroz")
            .scalar()
        )
        beans_id = (
            self.db.query(Ingredient.id)
            .filter(Ingredient.nombre == "Porotos")
            .scalar()
        )
        response = self.client.post(
            "/api/recetas/con-ingredientes",
            json={"ingredientes_ids": [rice_id, beans_id]},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(
            [recipe["id"] for recipe in response.json()],
            [self.recipe_ids["Arroz"], self.recipe_ids["Arroz con porotos"]],
        )
        self.assertIn("es_vegana", response.json()[0])

    def test_empty_or_unknown_ingredient_ids_return_no_recipes(self):
        for ingredient_ids in ([], [999999]):
            response = self.client.post(
                "/api/recetas/con-ingredientes",
                json={"ingredientes_ids": ingredient_ids},
            )
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json(), [])

    def test_rejects_non_positive_ids_and_extra_fields(self):
        invalid_id = self.client.post(
            "/api/recetas/con-ingredientes",
            json={"ingredientes_ids": [0]},
        )
        self.assertEqual(invalid_id.status_code, 422)

        extra_field = self.client.post(
            "/api/recetas/con-ingredientes",
            json={"ingredientes_ids": [1], "otra_cosa": True},
        )
        self.assertEqual(extra_field.status_code, 422)


if __name__ == "__main__":
    unittest.main()
