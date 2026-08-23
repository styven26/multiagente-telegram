"""Guardia de consentimiento. [Ciclo 1 - requisito ético]

Los botones inline de Telegram no caducan: un mensaje enviado hace semanas
sigue vivo en el chat y sus callbacks siguen llegando al bot. Verificar el
consentimiento solo en /menu deja abierta esa puerta — quien se retiró puede
volver a entrar desde un mensaje antiguo y seguir generando datos.

Este middleware intercepta TODO evento (comandos y callbacks por igual) antes
de que llegue a su handler. Solo /start queda exento, para que quien se retiró
pueda volver si lo decide.
"""

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update
from sqlalchemy import select

from app.db.base import SessionLocal
from app.db.models import Student

logger = logging.getLogger(__name__)

AVISO_SIN_REGISTRO = "Primero necesito tu registro. Escribe /start."
AVISO_RETIRADO = "Te retiraste del estudio. Escribe /start para volver."


def _es_start(evento: TelegramObject) -> bool:
    """El único camino que puede pasar sin consentimiento vigente."""
    if isinstance(evento, Message) and evento.text:
        return evento.text.split()[0].split("@")[0] == "/start"
    if isinstance(evento, CallbackQuery) and evento.data:
        return evento.data.startswith("consent:")
    return False


class ConsentimientoMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        evento: Update,
        datos: dict[str, Any],
    ) -> Any:
        interno = evento.event if isinstance(evento, Update) else evento

        if _es_start(interno):
            return await handler(evento, datos)

        usuario = datos.get("event_from_user")
        if usuario is None:
            return await handler(evento, datos)

        async with SessionLocal() as s:
            est = await s.scalar(
                select(Student).where(Student.telegram_id == usuario.id)
            )
            registrado = est is not None and est.consentimiento
            activo = est is not None and est.activo

        if registrado and activo:
            return await handler(evento, datos)

        aviso = AVISO_SIN_REGISTRO if not registrado else AVISO_RETIRADO
        logger.info("Evento bloqueado por consentimiento (tg_id=%s)", usuario.id)

        if isinstance(interno, CallbackQuery):
            await interno.answer(aviso, show_alert=True)
        elif isinstance(interno, Message):
            await interno.answer(aviso)

        return None