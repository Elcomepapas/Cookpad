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

## HU9 — Plan semanal

Los endpoints de planes semanales requieren autenticación Bearer y operan sobre
el plan del usuario autenticado:

- `POST /api/planes` crea un plan para `fecha_inicio` (debe ser lunes).
- `GET /api/planes/{plan_id}` devuelve el plan con sus recetas.
- `GET /api/planes/{plan_id}/lista-compras` suma los ingredientes del plan,
  escala las cantidades según las porciones planificadas, combina ingredientes
  repetidos y ordena alfabéticamente.
- `POST /api/planes/{plan_id}/recetas` agrega una receta con `dia_semana`,
  `comida` y `porciones`.
- `DELETE /api/planes/{plan_id}/recetas/{entry_id}` quita una receta del plan.

Solo puede existir un plan por usuario y fecha de inicio. Cada día y comida
admite una sola receta; los días van de 1 (lunes) a 7 (domingo), y las comidas
válidas son `desayuno`, `almuerzo`, `merienda` y `cena`.

## HU11 — Recetas con ingredientes disponibles

`POST /api/recetas/con-ingredientes` recibe un JSON como
`{"ingredientes_ids": [1, 2, 3]}` y devuelve las recetas que tienen al menos
un ingrediente y cuyos ingredientes están todos en esa lista. Si la lista está
vacía, devuelve una lista vacía. Esta consulta es pública.

## HU12 — Búsqueda y ordenación de recetas

`GET /api/recetas` permite buscar recetas por texto (`titulo` e `ingrediente`),
filtro de dificultad, tiempo máximo, valor de `vegana`, y ordenamiento por
`fecha` o `puntaje`. La respuesta sigue siendo una lista de `RecipeResponseDTO`
con los campos calculados (`es_vegana`, calorías y pasos) y mantiene la
compatibilidad de la API pública.

---

## Reglas de la arquitectura

1. `routers` no tocan la BD.
2. `services` no tocan `Request` / `Response`.
3. `repositories` no tienen lógica de negocio.
4. `models` no salen del repository / service.
5. `schemas` solo en routers.
6. Al cliente siempre va un DTO, nunca un Model.
