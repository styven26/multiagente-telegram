"""/perfil: resumen de avance del estudiante. [Ciclo 1]

Presenta al estudiante los datos que el sistema ya tiene sobre él: cápsulas
completadas, desempeño y dominio por tema. No muestra nombre ni correo — el
estudio es anónimo y el estudiante solo se identifica por su código.

El Agente Orquestador consulta y presenta; los datos provienen del Agente de
Evaluación (responses) y del Agente de Modelado del Estudiante (mastery).
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import Integer, func, select
from zoneinfo import ZoneInfo
from app.config import settings

from app.db.base import SessionLocal
from app.db.models import (
    Capsule, Mastery, Response, SpacedRepetition, Student, StudySession, Topic,
)

router = Router(name="perfil")

ANCHO_BARRA = 10


def _barra(nivel: float) -> str:
    """Barra de progreso en texto: Telegram no admite barras nativas."""
    llenos = round(nivel * ANCHO_BARRA)
    return "█" * llenos + "░" * (ANCHO_BARRA - llenos)


@router.message(Command("perfil"))
async def cmd_perfil(message: Message):
    async with SessionLocal() as s:
        est = await s.scalar(
            select(Student).where(Student.telegram_id == message.from_user.id)
        )
        if est is None:
            await message.answer("Primero necesito tu registro. Escribe /start.")
            return

        correcta = func.cast(Response.es_correcta, Integer)

        n_resp, n_ok = (await s.execute(
            select(func.count(Response.id),
                   func.coalesce(func.sum(correcta), 0))
            .where(Response.student_id == est.id)
        )).one()

        completadas = await s.scalar(
            select(func.count(func.distinct(StudySession.capsule_id)))
            .where(StudySession.student_id == est.id,
                   StudySession.completada.is_(True))
        ) or 0

        disponibles = await s.scalar(
            select(func.count(Capsule.id)).where(Capsule.activo.is_(True))
        ) or 0

        filas = (await s.execute(
            select(Topic.nombre, Mastery.nivel, Mastery.numero_evidencias)
            .join(Mastery, Mastery.topic_id == Topic.id)
            .where(Mastery.student_id == est.id)
            .order_by(Topic.orden)
        )).all()

        proximo = await s.scalar(
            select(func.min(SpacedRepetition.proxima_revision_en))
            .where(SpacedRepetition.student_id == est.id,
                   SpacedRepetition.activo.is_(True))
        )

    acierto = (n_ok / n_resp) if n_resp else 0.0

    lineas = [
        "👤 <b>Tu perfil</b>",
        f"Código: <code>{est.codigo_anonimo}</code>",
        "",
        "📊 <b>Rendimiento</b>",
        f"Cápsulas completadas: <b>{completadas}</b> de {disponibles}",
        f"Respuestas correctas: <b>{int(n_ok)}</b>",
        f"Respuestas incorrectas: <b>{n_resp - int(n_ok)}</b>",
        f"Tasa de acierto: <b>{acierto:.0%}</b>",
    ]

    if filas:
        lineas += ["", "📚 <b>Dominio por tema</b>"]
        for nombre, nivel, evidencias in filas:
            lineas.append(f"{_barra(nivel)} {nivel:.0%}  {nombre}")

    if proximo is not None:
        local = proximo.astimezone(ZoneInfo(settings.TIMEZONE))
        lineas += ["", f"🔁 Próximo repaso: <b>{local:%d/%m a las %H:%M}</b>"]

    await message.answer("\n".join(lineas))