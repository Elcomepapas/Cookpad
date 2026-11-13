from datetime import datetime
from typing import Literal

from pydantic import BaseModel


CategoriaTutorial = Literal["tecnicas", "cortes", "reposteria", "basicos", "recetas"]


class TutorialResponseDTO(BaseModel):
    id: int
    titulo: str
    descripcion: str | None
    video_url: str
    miniatura_url: str | None
    categoria: CategoriaTutorial
    duracion_seg: int | None
    receta_id: int | None
    fecha_publicacion: datetime

    model_config = {"from_attributes": True}
