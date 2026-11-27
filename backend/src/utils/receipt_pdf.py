from datetime import date
from decimal import Decimal, InvalidOperation
from io import BytesIO
import re

from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError

from src.dtos.fridge_dto import ReceiptPreviewDTO, ReceiptProductPreviewDTO
from src.utils.errors import BadRequestError

MAX_RECEIPT_BYTES = 5 * 1024 * 1024
MAX_RECEIPT_PAGES = 10
MAX_RECEIPT_PRODUCTS = 100

_PRODUCT_COLUMNS_PATTERN = re.compile(
    r"^PRODUCTO\s+(.+?)\s+([\d.,]+)\s+(g|ml|unidad)\s+"
    r"\$?([\d.,]+)(?:\s+(\d{4}-\d{2}-\d{2}|SIN VENCIMIENTO|NO APLICA|—|-))?$",
    re.IGNORECASE,
)


def _parse_decimal(value: str) -> Decimal:
    normalized = value.strip().replace("$", "").replace(" ", "")
    if "," in normalized and "." in normalized:
        # Interpreta el último separador como decimal: 2.200,00 o 2,200.00.
        decimal_separator = "," if normalized.rfind(",") > normalized.rfind(".") else "."
        thousands_separator = "." if decimal_separator == "," else ","
        normalized = normalized.replace(thousands_separator, "")
        if decimal_separator == ",":
            normalized = normalized.replace(",", ".")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")
    return Decimal(normalized)


def _read_header(line: str, label: str) -> str | None:
    legacy_fields = line.split("|")
    if len(legacy_fields) == 2 and legacy_fields[0].strip().upper() == label:
        return legacy_fields[1].strip()

    match = re.match(rf"^{label}\s*:\s*(.+)$", line, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    match = re.match(rf"^{label}\s{{1,}}(.+)$", line, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _parse_product_line(line: str) -> tuple[str, Decimal, str, Decimal, date | None]:
    if "|" in line:
        fields = line.split("|")
        if len(fields) != 6 or fields[0].strip().upper() != "PRODUCTO":
            raise ValueError("Invalid legacy product row")
        name, raw_quantity, unit, raw_price, raw_expiry = (
            field.strip() for field in fields[1:]
        )
    else:
        match = _PRODUCT_COLUMNS_PATTERN.fullmatch(line.strip())
        if match is None:
            raise ValueError("Invalid product columns")
        name, raw_quantity, unit, raw_price, raw_expiry = match.groups()
        name = name.strip()
        unit = unit.lower()

    quantity = _parse_decimal(raw_quantity)
    price = _parse_decimal(raw_price)
    expiry_text = raw_expiry.strip() if raw_expiry else ""
    expiry = (
        date.fromisoformat(expiry_text)
        if expiry_text and expiry_text.upper() not in {"SIN VENCIMIENTO", "NO APLICA", "—", "-"}
        else None
    )
    if not name or unit not in {"g", "ml", "unidad"}:
        raise ValueError("Invalid product name or unit")
    if quantity <= 0 or price < 0:
        raise ValueError("Invalid product quantity or price")
    return name, quantity, unit, price, expiry


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
    if not lines:
        raise BadRequestError("Receipt must use the Cookpad receipt format")

    first_line = lines[0].upper()
    accepted_titles = {
        "COOKPAD_RECIBO|1",  # formato anterior, se conserva para PDFs ya creados
        "RECIBO DE COMPRA",
        "RECIBO DE COMPRA - COOKPAD",
        "TICKET DE COMPRA",
        "TICKET DE COMPRA - COOKPAD",
    }
    if first_line not in accepted_titles:
        raise BadRequestError("Receipt must use the Cookpad receipt format")

    commerce: str | None = None
    purchase_date: date | None = None
    products: list[ReceiptProductPreviewDTO] = []

    try:
        for line in lines[1:]:
            upper_line = line.upper()
            if "CANTIDAD" in upper_line and "UNIDAD" in upper_line and "PRECIO" in upper_line:
                continue

            parsed_commerce = _read_header(line, "COMERCIO")
            if parsed_commerce is not None and commerce is None:
                commerce = parsed_commerce
                continue

            parsed_date = _read_header(line, "FECHA")
            if parsed_date is not None and purchase_date is None:
                purchase_date = date.fromisoformat(parsed_date)
                continue

            if line.upper().startswith("PRODUCTO"):
                if len(products) >= MAX_RECEIPT_PRODUCTS:
                    raise BadRequestError("Receipt cannot contain more than 100 products")
                name, quantity, unit, price, expiry = _parse_product_line(line)
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
                continue

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
