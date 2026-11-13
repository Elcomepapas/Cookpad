import bcrypt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    pbkdf2_sha256__default_rounds=600_000,
)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    # Mantiene el acceso a cuentas creadas cuando el sistema usaba bcrypt.
    if hashed.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("ascii"))
        except (ValueError, TypeError, UnicodeEncodeError):
            return False

    try:
        return pwd_context.verify(plain, hashed)
    except (UnknownHashError, ValueError, TypeError):
        return False
