"""Disociación telegram_id -> codigo_anonimo (protocolo CEISH)."""

import hashlib

from app.config import settings


def generar_codigo_anonimo(telegram_id: int) -> str:
    """Código estable e irreversible sin la sal. 12 caracteres."""
    base = f"{settings.ANON_SALT}:{telegram_id}".encode("utf-8")
    return hashlib.sha256(base).hexdigest()[:12].upper()