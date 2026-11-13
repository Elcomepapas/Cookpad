from fastapi import APIRouter, Depends, File, Path, UploadFile, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.usuario_model import User
from src.dtos.fridge_dto import (
    FridgeOverviewDTO,
    FridgeItemDTO,
    PurchaseDTO,
    ReceiptPreviewDTO,
    RecipeShoppingSuggestionDTO,
    ShoppingReminderDTO,
)
from src.middlewares.auth_middleware import get_current_user
from src.schemas.fridge_schema import (
    AddShoppingRemindersSchema,
    CreatePurchaseSchema,
    UpdateFridgeCategorySchema,
)
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


@router.patch("/productos/{item_id}", response_model=FridgeItemDTO)
def update_fridge_product_category(
    payload: UpdateFridgeCategorySchema,
    item_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FridgeService(db).update_item_category(
        current_user.id, item_id, payload
    )


@router.get(
    "/sugerencias", response_model=list[RecipeShoppingSuggestionDTO]
)
def get_shopping_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FridgeService(db).suggestions(current_user.id)


@router.get(
    "/recordatorios", response_model=list[ShoppingReminderDTO]
)
def list_shopping_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FridgeService(db).list_reminders(current_user.id)


@router.post(
    "/recordatorios",
    response_model=list[ShoppingReminderDTO],
    status_code=status.HTTP_201_CREATED,
)
def add_shopping_reminders(
    payload: AddShoppingRemindersSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FridgeService(db).add_reminders(current_user.id, payload)


@router.delete(
    "/recordatorios/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_shopping_reminder(
    reminder_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    FridgeService(db).delete_reminder(current_user.id, reminder_id)
