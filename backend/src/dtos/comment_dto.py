from datetime import datetime

from pydantic import BaseModel


class CommentDTO(BaseModel):
    texto: str
    puntaje: int


class CommentResponseDTO(BaseModel):
    id: int
    usuario_id: int
    receta_id: int
    texto: str
    puntaje: int
    fecha: datetime
    fecha_edicion: datetime | None = None

    model_config = {"from_attributes": True}
