from pathlib import Path
from typing import BinaryIO
from uuid import UUID

from src.utils.errors import BadRequestError

VIDEO_DIRECTORY = Path(__file__).resolve().parents[2] / ".tutorial-videos"
MAX_VIDEO_BYTES = 50 * 1024 * 1024


def video_path(video_id: UUID) -> Path:
    return VIDEO_DIRECTORY / f"{video_id}.mp4"


def save_video(
    video_id: UUID, stream: BinaryIO, filename: str | None, size: int | None,
) -> Path:
    if not filename or not filename.lower().endswith(".mp4"):
        raise BadRequestError("Seleccioná un archivo MP4.")
    if size is not None and size > MAX_VIDEO_BYTES:
        raise BadRequestError("El video no puede superar los 50 MB.")

    # MP4 files begin with an ISO base media file type box.
    header = stream.read(16)
    if len(header) != 16 or header[4:8] != b"ftyp" or int.from_bytes(header[:4], "big") < 16:
        raise BadRequestError("El archivo no tiene un encabezado MP4 válido.")

    path = video_path(video_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        try:
            total = len(header)
            output.write(header)
            while chunk := stream.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_VIDEO_BYTES:
                    raise BadRequestError("El video no puede superar los 50 MB.")
                output.write(chunk)
        except Exception:
            output.close()
            path.unlink(missing_ok=True)
            raise
    return path
