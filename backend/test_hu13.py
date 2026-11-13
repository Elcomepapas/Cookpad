"""Pruebas de tutoriales en video: python -m unittest test_hu13 -v."""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "hu13-test-secret"

import unittest
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.app import app
from src.db.connection import Base, get_db
from src.db.models.receta_model import Recipe
from src.db.models.tutorial_model import Tutorial
from src.db.models.usuario_model import User


class TutorialTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

        user = User(email="tutorial@example.com", nombre="Tutorial", password_hash="test")
        self.db.add(user)
        self.db.flush()
        recipe = Recipe(
            autor_id=user.id,
            titulo="Receta asociada",
            porciones=2,
            tiempo_min=20,
            dificultad="facil",
        )
        self.db.add(recipe)
        self.db.flush()
        self.recipe_id = recipe.id
        self.tutorial_id = 1
        self.db.add_all(
            [
                Tutorial(
                    titulo="Picar cebolla",
                    descripcion="Una técnica de corte.",
                    video_url="https://videos.example.com/cebolla.mp4",
                    categoria="cortes",
                    orden=2,
                    receta_id=recipe.id,
                    fecha_publicacion=datetime(2026, 1, 2),
                ),
                Tutorial(
                    titulo="Técnicas de repostería",
                    descripcion=None,
                    video_url="https://videos.example.com/reposteria.mp4",
                    categoria="reposteria",
                    orden=1,
                    fecha_publicacion=datetime(2026, 1, 1),
                ),
            ]
        )
        self.db.commit()
        self.tutorial_id = self.db.query(Tutorial).filter_by(titulo="Picar cebolla").one().id

        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()
        self.engine.dispose()

    def test_list_filters_and_orders_tutorials(self):
        response = self.client.get("/api/tutoriales?categoria=cortes&q=cebolla")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["titulo"] for item in response.json()], ["Picar cebolla"])
        self.assertEqual(response.json()[0]["video_url"], "https://videos.example.com/cebolla.mp4")

        self.assertEqual(
            [item["titulo"] for item in self.client.get("/api/tutoriales").json()],
            ["Técnicas de repostería", "Picar cebolla"],
        )
        self.assertEqual(self.client.get("/api/tutoriales?categoria=invalida").status_code, 422)

    def test_get_tutorial_and_report_missing_id(self):
        self.assertEqual(
            self.client.get(f"/api/tutoriales/{self.tutorial_id}").json()["titulo"],
            "Picar cebolla",
        )
        self.assertEqual(self.client.get("/api/tutoriales/999").status_code, 404)

    def test_list_tutorials_for_recipe_and_report_missing_recipe(self):
        response = self.client.get(f"/api/recetas/{self.recipe_id}/tutoriales")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["titulo"] for item in response.json()], ["Picar cebolla"])
        self.assertEqual(self.client.get("/api/recetas/999/tutoriales").status_code, 404)


if __name__ == "__main__":
    unittest.main()
