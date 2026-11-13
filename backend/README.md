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

## Tutoriales en video

- `GET /api/tutoriales?categoria=cortes&q=cebolla` lista tutoriales y permite filtrar por categoría y texto del título.
- `GET /api/tutoriales/{id}` devuelve un tutorial o `404` si no existe.
- `GET /api/recetas/{id}/tutoriales` lista los videos de una receta; devuelve `404` si la receta no existe.

El backend devuelve la URL directa al archivo MP4 para reproducirlo en el navegador; no aloja ni transmite los videos. Para habilitar la tabla, ejecutá el bloque de tutoriales de `src/db/tables.sql` en PostgreSQL y cargá URLs reales directas a archivos MP4.

## Mi heladera

- `POST /api/heladera/recibos/preview` recibe un PDF, interpreta el formato simulado y propone coincidencias con ingredientes del catálogo.
- `POST /api/heladera/compras` guarda la compra confirmada, con sus productos y vencimientos.
- `GET /api/heladera` devuelve las compras agrupadas por comercio y el gasto acumulado del usuario.
- `PATCH /api/heladera/productos/{id}` cambia la categoría de un producto propio, incluso después de cargar una compra.
- `GET /api/heladera/sugerencias` compara solo los ingredientes vigentes en la heladera con recetas guardadas por ese usuario. Sugiere recetas con al menos un ingrediente disponible y otros por comprar.
- `GET /api/heladera/recordatorios`, `POST /api/heladera/recordatorios` y `DELETE /api/heladera/recordatorios/{id}` permiten gestionar la lista manual de productos para recordar.

El PDF debe contener texto legible en este formato, una instrucción por línea:

```text
COOKPAD_RECIBO|1
COMERCIO|Supermercado
FECHA|2026-11-13
PRODUCTO|Arroz|500|g|1800.00|2026-12-01
PRODUCTO|Cebolla|2|unidad|700.00|
```

Los precios son el total por línea. Se admiten hasta 100 productos, tres unidades (`g`, `ml`, `unidad`) y PDFs de hasta 5 MB/10 páginas. El usuario revisa el resultado, vincula cada producto con un ingrediente del catálogo y puede completar los vencimientos que falten. El PDF se procesa en memoria y no se conserva. Los productos que vencen hoy o en los próximos siete días se marcan como próximos a vencer; los vencidos no cuentan como disponibles para sugerencias.

Al revisar cada compra, el usuario elige la categoría de cada producto: bebidas, aderezos, lácteos, verduras, frutas, panificados, almacén, congelados u otros. Las carnes se separan en vacuna, porcina, aves, ovina, pescados, mariscos, fiambres y otras carnes.

La lista de recordatorios se completa manualmente desde la pantalla de la heladera. Se pueden escribir varios productos, uno por renglón; las entradas repetidas no se duplican y cada usuario solo puede consultar o eliminar sus propios recordatorios.

---

## Reglas de la arquitectura

1. `routers` no tocan la BD.
2. `services` no tocan `Request` / `Response`.
3. `repositories` no tienen lógica de negocio.
4. `models` no salen del repository / service.
5. `schemas` solo en routers.
6. Al cliente siempre va un DTO, nunca un Model.
