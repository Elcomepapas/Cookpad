from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.usuario_model import User
from src.dtos.fridge_dto import (
    FridgeOverviewDTO,
    PurchaseDTO,
    ReceiptPreviewDTO,
    RecipeShoppingSuggestionDTO,
)
from src.middlewares.auth_middleware import get_current_user
from src.schemas.fridge_schema import CreatePurchaseSchema
from src.services.fridge_service import FridgeService
from src.utils.errors import BadRequestError
from src.utils.receipt_pdf import MAX_RECEIPT_BYTES

router = APIRouter(prefix="/heladera", tags=["heladera"])


@router.post("/recibos/preview", response_model=ReceiptPreviewDTO)
async def preview_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise BadRequestError("Upload a PDF receipt")
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise BadRequestError("Upload a valid PDF receipt")
    content = await file.read(MAX_RECEIPT_BYTES + 1)
    return FridgeService(db).preview_receipt(content)


@router.post(
    "/compras",
    response_model=PurchaseDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase(
    payload: CreatePurchaseSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FridgeService(db).create_purchase(current_user.id, payload)


@router.get("", response_model=FridgeOverviewDTO)
def get_fridge(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FridgeService(db).overview(current_user.id)


@router.get(
    "/sugerencias", response_model=list[RecipeShoppingSuggestionDTO]
)
def get_shopping_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FridgeService(db).suggestions(current_user.id)
