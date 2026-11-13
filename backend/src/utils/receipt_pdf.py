from datetime import date
from decimal import Decimal, InvalidOperation
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError

from src.dtos.fridge_dto import ReceiptPreviewDTO, ReceiptProductPreviewDTO
from src.utils.errors import BadRequestError

MAX_RECEIPT_BYTES = 5 * 1024 * 1024
MAX_RECEIPT_PAGES = 10
MAX_RECEIPT_PRODUCTS = 100


def extract_receipt_text(content: bytes) -> str:
    if not content or len(content) > MAX_RECEIPT_BYTES:
        raise BadRequestError("Receipt PDF must be between 1 byte and 5 MB")
    try:
        reader = PdfReader(BytesIO(content), strict=True)
        if len(reader.pages) > MAX_RECEIPT_PAGES:
            raise BadRequestError("Receipt PDF cannot contain more than 10 pages")
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except (PdfReadError, PdfStreamError, OSError, ValueError) as exc:
        raise BadRequestError("Could not read the receipt PDF") from exc

    if not text.strip():
        raise BadRequestError("Receipt PDF contains no readable text")
    return text


def parse_receipt_text(text: str) -> ReceiptPreviewDTO:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or lines[0] != "COOKPAD_RECIBO|1":
        raise BadRequestError("Receipt must use the Cookpad fixed PDF format")

    commerce: str | None = None
    purchase_date: date | None = None
    products: list[ReceiptProductPreviewDTO] = []

    try:
        for line in lines[1:]:
            fields = line.split("|")
            if fields[0] == "COMERCIO" and len(fields) == 2 and commerce is None:
                commerce = fields[1].strip()
            elif fields[0] == "FECHA" and len(fields) == 2 and purchase_date is None:
                purchase_date = date.fromisoformat(fields[1].strip())
            elif fields[0] == "PRODUCTO" and len(fields) == 6:
                if len(products) >= MAX_RECEIPT_PRODUCTS:
                    raise BadRequestError("Receipt cannot contain more than 100 products")
                name = fields[1].strip()
                quantity = Decimal(fields[2].strip())
                unit = fields[3].strip()
                price = Decimal(fields[4].strip())
                expiry = date.fromisoformat(fields[5].strip()) if fields[5].strip() else None
                if not name or unit not in {"g", "ml", "unidad"}:
                    raise ValueError("Invalid product name or unit")
                if quantity <= 0 or price < 0:
                    raise ValueError("Invalid product quantity or price")
                products.append(
                    ReceiptProductPreviewDTO(
                        nombre=name,
                        ingrediente_id=None,
                        cantidad=quantity,
                        unidad=unit,
                        precio_total=price,
                        fecha_vencimiento=expiry,
                    )
                )
            else:
                raise ValueError("Invalid receipt row")
    except (InvalidOperation, ValueError) as exc:
        raise BadRequestError(
            "Receipt has invalid fields; check dates, prices, quantities, and row format"
        ) from exc

    if not commerce or len(commerce) > 120 or purchase_date is None or not products:
        raise BadRequestError("Receipt needs a store, purchase date, and at least one product")
    return ReceiptPreviewDTO(
        comercio=commerce,
        fecha_compra=purchase_date,
        productos=products,
    )
