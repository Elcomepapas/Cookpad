from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from src.db.connection import Base


class Tutorial(Base):
    __tablename__ = "tutorial"

    id = Column(Integer, primary_key=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=False)
    miniatura_url = Column(String(500), nullable=True)
    categoria = Column(String(30), nullable=False, default="tecnicas")
    duracion_seg = Column(Integer, nullable=True)
    receta_id = Column(Integer, ForeignKey("receta.id", ondelete="SET NULL"), nullable=True)
    orden = Column(Integer, nullable=False, default=0)
    fecha_publicacion = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("video_url", name="uq_tutorial_video_url"),
        CheckConstraint(
            r"video_url ~* '^https?://.+\.mp4(\?.*)?$'",
            name="ck_tutorial_mp4",
        ).ddl_if(dialect="postgresql"),
        CheckConstraint(
            "categoria IN ('tecnicas', 'cortes', 'reposteria', 'basicos', 'recetas')",
            name="ck_tutorial_categoria",
        ),
        CheckConstraint(
            "duracion_seg IS NULL OR duracion_seg > 0",
            name="ck_tutorial_duracion",
        ),
    )
