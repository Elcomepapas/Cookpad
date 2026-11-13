"""Pruebas de tutoriales en video: python -m unittest test_hu13 -v."""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "hu13-test-secret"

import unittest
from datetime import datetime

import bcrypt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.app import app
from src.db.connection import Base, get_db
from src.db.models.receta_model import Recipe
from src.db.models.tutorial_model import Tutorial
from src.db.models.usuario_model import User
from src.middlewares.auth_middleware import get_current_user
from src.utils.hash import hash_password, verify_password


class TutorialTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

        self.user = User(
            email="tutorial@example.com",
            nombre="Tutorial",
            password_hash="test",
            es_admin=True,
        )
        self.non_admin = User(
            email="reader@example.com",
            nombre="Reader",
            password_hash="test",
        )
        self.db.add_all([self.user, self.non_admin])
        self.db.flush()
        recipe = Recipe(
            autor_id=self.user.id,
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
        app.dependency_overrides[get_current_user] = lambda: self.user
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

    def test_admin_can_add_video_url_and_regular_user_cannot(self):
        payload = {
            "titulo": "Cortar cebolla",
            "descripcion": "Técnica básica",
            "video_url": "https://videos.example.com/cortar-cebolla.mp4",
            "categoria": "cortes",
            "receta_id": self.recipe_id,
            "duracion_seg": 90,
            "orden": 1,
        }
        created = self.client.post("/api/tutoriales", json=payload)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["video_url"], payload["video_url"])
        self.assertEqual(self.client.post("/api/tutoriales", json=payload).status_code, 409)

        app.dependency_overrides[get_current_user] = lambda: self.non_admin
        denied = self.client.post(
            "/api/tutoriales",
            json={**payload, "video_url": "https://videos.example.com/otro.mp4"},
        )
        self.assertEqual(denied.status_code, 403)

        app.dependency_overrides[get_current_user] = lambda: self.user
        invalid_url = self.client.post(
            "/api/tutoriales", json={**payload, "video_url": "https://example.com/watch?id=1"}
        )
        self.assertEqual(invalid_url.status_code, 422)

    def test_registration_and_login_match_frontend_auth_contract(self):
        account = {
            "email": "new-user@example.com",
            "nombre": "New User",
            "password": "secure-password-123",
        }
        registered = self.client.post("/api/auth/register", json=account)
        self.assertEqual(registered.status_code, 201)
        self.assertFalse(registered.json()["es_admin"])
        self.assertNotIn("password_hash", registered.json())

        logged_in = self.client.post(
            "/api/auth/login",
            json={"email": account["email"], "password": account["password"]},
        )
        self.assertEqual(logged_in.status_code, 200)
        self.assertTrue(logged_in.json()["access_token"])
        self.assertEqual(logged_in.json()["usuario"]["email"], account["email"])
        self.assertFalse(logged_in.json()["usuario"]["es_admin"])

    def test_frontend_origin_is_allowed_by_cors(self):
        response = self.client.options(
            "/api/tutoriales",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["access-control-allow-origin"],
            "http://localhost:5173",
        )

    def test_password_hashing_works_and_keeps_legacy_bcrypt_compatible(self):
        current_hash = hash_password("new-password")
        self.assertTrue(verify_password("new-password", current_hash))
        self.assertFalse(verify_password("wrong-password", current_hash))

        legacy_hash = bcrypt.hashpw(b"old-password", bcrypt.gensalt()).decode("ascii")
        self.assertTrue(verify_password("old-password", legacy_hash))


if __name__ == "__main__":
    unittest.main()
