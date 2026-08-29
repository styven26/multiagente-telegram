"""Planificador del Agente de Repetición Espaciada."""

import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.db.base import SessionLocal
from app.agents.spaced_repetition import reminder_service
from app.services import session_service

logger = logging.getLogger(__name__)

INTERVALO_MINUTOS = 5


async def ciclo_repasos(bot: Bot) -> None:
    try:
        async with SessionLocal() as s:
            creados = await reminder_service.generar_pendientes(s)
            enviados = await reminder_service.enviar_pendientes(bot, s)
        if creados or enviados:
            logger.info("Repasos: %s programados, %s enviados", creados, enviados)
    except Exception:                                # noqa: BLE001
        # Nunca dejar que un fallo tumbe el planificador: se reintenta al
        # siguiente ciclo.
        logger.exception("Error en el ciclo de repasos")


async def ciclo_sesiones() -> None:
    try:
        async with SessionLocal() as s:
            cerradas = await session_service.cerrar_abandonadas(s)
        if cerradas:
            logger.info("Sesiones abandonadas cerradas: %s", cerradas)
    except Exception:                                # noqa: BLE001
        logger.exception("Error cerrando sesiones abandonadas")


def crear_scheduler(bot: Bot) -> AsyncIOScheduler:
    sch = AsyncIOScheduler(timezone=settings.TIMEZONE)

    sch.add_job(
        ciclo_repasos, "interval",
        minutes=INTERVALO_MINUTOS, id="ciclo_repasos",
        args=[bot],
        max_instances=1, coalesce=True,
    )

    sch.add_job(
        ciclo_sesiones, "interval",
        minutes=15, id="ciclo_sesiones",
        max_instances=1, coalesce=True,
    )
    return sch