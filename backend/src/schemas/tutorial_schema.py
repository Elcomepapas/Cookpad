from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from src.dtos.tutorial_dto import CategoriaTutorial


class CreateTutorialSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str = Field(min_length=1, max_length=200)
    descripcion: str | None = None
    video_url: HttpUrl = Field(max_length=500)
    miniatura_url: HttpUrl | None = Field(default=None, max_length=500)
    categoria: CategoriaTutorial = "tecnicas"
    duracion_seg: int | None = Field(default=None, gt=0)
    receta_id: int | None = Field(default=None, gt=0)
    orden: int = Field(default=0, ge=0)

    @field_validator("titulo")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        title = value.strip()
        if not title:
            raise ValueError("Tutorial title cannot be blank")
        return title

    @field_validator("descripcion")
    @classmethod
    def empty_description_becomes_null(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    @field_validator("video_url")
    @classmethod
    def video_must_be_direct_mp4(cls, value: HttpUrl) -> HttpUrl:
        if not urlparse(str(value)).path.lower().endswith(".mp4"):
            raise ValueError("Video URL must point directly to an MP4 file")
        return value
