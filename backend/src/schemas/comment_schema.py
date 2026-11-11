from pydantic import BaseModel, Field, field_validator


class CommentSchema(BaseModel):
    texto: str = Field(min_length=1)
    puntaje: int = Field(ge=1, le=5, strict=True)

    model_config = {"extra": "forbid"}

    @field_validator("texto")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El comentario no puede estar vacío")
        return value
