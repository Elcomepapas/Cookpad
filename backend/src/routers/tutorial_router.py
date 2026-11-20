from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.usuario_model import User
from src.dtos.tutorial_dto import (
    CategoriaTutorial,
    CreateTutorialDTO,
    TutorialResponseDTO,
)
from src.middlewares.auth_middleware import get_current_user
from src.schemas.tutorial_schema import CreateTutorialSchema
from src.services.tutorial_service import TutorialService
from src.utils.errors import BadRequestError, NotFoundError
from src.utils.tutorial_video import video_path

router = APIRouter(tags=["tutoriales"])


@router.post(
    "/tutoriales",
    response_model=TutorialResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_tutorial(
    payload: CreateTutorialSchema,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    dto = CreateTutorialDTO(**payload.model_dump(mode="json"))
    return TutorialService(db).create(dto)


@router.post(
    "/tutoriales/videos",
    response_model=TutorialResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def upload_tutorial_video(
    request: Request,
    file: Annotated[UploadFile, File()],
    titulo: Annotated[str, Form(min_length=1, max_length=200)],
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
    categoria: Annotated[CategoriaTutorial, Form()] = "tecnicas",
    descripcion: Annotated[str | None, Form(max_length=2000)] = None,
    receta_id: Annotated[int | None, Form(gt=0)] = None,
):
    video_id = uuid4()
    url = request.url_for("get_tutorial_video", video_id=str(video_id))
    try:
        payload = CreateTutorialSchema(
            titulo=titulo, video_url=str(url), categoria=categoria,
            descripcion=descripcion, receta_id=receta_id,
        )
    except ValidationError as exc:
        raise BadRequestError(exc.errors()[0]["msg"]) from exc

    dto = CreateTutorialDTO(**payload.model_dump(mode="json"))
    return TutorialService(db).create_uploaded(dto, video_id, file.file, file.filename, file.size)


@router.get("/tutoriales/videos/{video_id}.mp4", response_class=FileResponse)
def get_tutorial_video(video_id: UUID):
    path = video_path(video_id)
    if not path.is_file():
        raise NotFoundError("Video no encontrado")
    return FileResponse(path, media_type="video/mp4", headers={"X-Content-Type-Options": "nosniff"})


@router.get("/tutoriales", response_model=list[TutorialResponseDTO])
def list_tutorials(
    categoria: CategoriaTutorial | None = None,
    query: Annotated[
        str | None, Query(alias="q", max_length=200, description="Buscar en el título")
    ] = None,
    db: Session = Depends(get_db),
):
    return TutorialService(db).list_all(categoria, query)


@router.get("/tutoriales/{tutorial_id}", response_model=TutorialResponseDTO)
def get_tutorial(tutorial_id: int, db: Session = Depends(get_db)):
    return TutorialService(db).get_by_id(tutorial_id)


@router.get(
    "/recetas/{recipe_id}/tutoriales", response_model=list[TutorialResponseDTO]
)
def list_recipe_tutorials(recipe_id: int, db: Session = Depends(get_db)):
    return TutorialService(db).list_for_recipe(recipe_id)
