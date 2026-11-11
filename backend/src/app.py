from fastapi import FastAPI

from src.middlewares.error_middleware import app_error_handler
from src.routers import auth_router, ingredient_router, recipe_router, user_router
from src.routers import saved_recipe_router
from src.routers import comment_router
from src.utils.errors import AppError

app = FastAPI(title="Cookpad API")

app.add_exception_handler(AppError, app_error_handler)

app.include_router(user_router.router, prefix="/api")
app.include_router(auth_router.router, prefix="/api")
app.include_router(ingredient_router.router, prefix="/api")
app.include_router(recipe_router.router, prefix="/api")
app.include_router(saved_recipe_router.router, prefix="/api")
app.include_router(comment_router.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
