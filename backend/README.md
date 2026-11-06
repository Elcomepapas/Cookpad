# Cookpad — Backend (FastAPI + SQLAlchemy + Pydantic)

Backend del proyecto Cookpad, organizado en capas (routers, services, repositories, models, schemas, DTOs y mappers).

La API conserva los módulos de usuarios y autenticación, y los modelos de ingredientes y recetas. Los DTOs de respuesta y mappers están en sus carpetas respectivas.

---

## Setup

```bash
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\Activate.ps1       # Windows

pip install -r requirements.txt
cp .env.example .env               # editá con tus credenciales

uvicorn src.app:app --reload
```

Abrir http://localhost:8000/docs para ver Swagger.

---

## Estructura de carpetas

```
src/
├── db/
│   ├── connection.py
│   ├── models/          # SQLAlchemy
│   ├── migrations/      # Alembic
│   └── seeders/
├── schemas/             # Pydantic (validación HTTP)
├── dtos/                # Pydantic (transporte entre capas)
├── mappers/             # Model ⇄ DTO
├── repositories/        # queries
├── services/            # lógica de negocio
├── routers/             # endpoints FastAPI
├── middlewares/
├── config/
├── utils/
├── app.py               # crea app FastAPI
└── main.py              # entry point
```

---

## Estado actual

Los endpoints de registro e inicio de sesión están disponibles bajo `/api/users` y `/api/auth`. Los modelos de ingredientes y recetas ya están definidos; sus endpoints y lógica de negocio se pueden implementar a partir de las consignas del proyecto.

---

## Reglas de la arquitectura

1. `routers` no tocan la BD.
2. `services` no tocan `Request` / `Response`.
3. `repositories` no tienen lógica de negocio.
4. `models` no salen del repository / service.
5. `schemas` solo en routers.
6. Al cliente siempre va un DTO, nunca un Model.
