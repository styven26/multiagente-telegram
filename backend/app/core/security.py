"""Hash de contraseñas y emisión/verificación de JWT."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings

ALGORITMO = "HS256"


def hash_password(password: str) -> str:
    datos = password.encode("utf-8")
    if len(datos) > 72:
        raise ValueError("La contraseña no puede superar 72 bytes")
    return bcrypt.hashpw(datos, bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, hash_guardado: str | None) -> bool:
    if not hash_guardado:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hash_guardado.encode("utf-8"))
    except ValueError:
        return False


def crear_token(teacher_id: int, rol: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(teacher_id),
        "rol": rol,
        "iat": ahora,
        "exp": ahora + timedelta(hours=settings.JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITMO)


def decodificar_token(token: str) -> dict:
    """Lanza jwt.PyJWTError si es inválido o expiró."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITMO])