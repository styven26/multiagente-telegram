"""/repasos: lista de repasos pendientes del estudiante. [Ciclo 1]

Reemplaza el envío de un recordatorio por cada cápsula vencida: el estudiante
recibe un solo aviso y entra aquí a ver todo lo que le toca. Evita que alguien
con cuatro repasos vencidos reciba cuatro mensajes seguidos, que es la vía más
rápida a que silencie el bot.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, Message,
)
from sqlalchemy import select

from app.agents.base import estudiante_por_telegram as _estudiante
from app.config import settings
from app.db.base import SessionLocal
from app.db.models import Capsule, SpacedRepetition

router = Router(name="repasos")

MAX_LISTA = 10


async def _pendientes(s, student_id: int):
    """Repasos vencidos, del más atrasado al más reciente."""
    ahora = datetime.now(timezone.utc)
    return (await s.execute(
        select(SpacedRepetition.capsule_id, Capsule.titulo,
               Capsule.duracion_min, SpacedRepetition.proxima_revision_en)
        .join(Capsule, Capsule.id == SpacedRepetition.capsule_id)
        .where(SpacedRepetition.student_id == student_id,
               SpacedRepetition.activo.is_(True),
               Capsule.activo.is_(True),
               SpacedRepetition.proxima_revision_en <= ahora)
        .order_by(SpacedRepetition.proxima_revision_en)
        .limit(MAX_LISTA)
    )).all()


async def _proximo(s, student_id: int):
    """El repaso más cercano aún no vencido, para orientar al que está al día."""
    ahora = datetime.now(timezone.utc)
    return await s.scalar(
        select(SpacedRepetition.proxima_revision_en)
        .join(Capsule, Capsule.id == SpacedRepetition.capsule_id)
        .where(SpacedRepetition.student_id == student_id,
               SpacedRepetition.activo.is_(True),
               Capsule.activo.is_(True),
               SpacedRepetition.proxima_revision_en > ahora)
        .order_by(SpacedRepetition.proxima_revision_en)
        .limit(1)
    )


async def contar_pendientes(s, student_id: int) -> int:
    """Lo usa el menú para mostrar el número junto al botón."""
    filas = await _pendientes(s, student_id)
    return len(filas)


@router.message(Command("repasos"))
async def cmd_repasos(message: Message):
    async with SessionLocal() as s:
        est = await _estudiante(s, message.from_user.id)
        if est is None:
            await message.answer("Primero necesito tu registro. Escribe /start.")
            return

        filas = await _pendientes(s, est.id)
        proximo = await _proximo(s, est.id) if not filas else None

    if not filas:
        texto = "🔁 <b>Repasos</b>\n\nNo tienes repasos pendientes."
        if proximo is not None:
            local = proximo.astimezone(ZoneInfo(settings.TIMEZONE))
            texto += f"\n\nEl siguiente será el <b>{local:%d/%m}</b>."
        await message.answer(texto)
        return

    plural = "repaso pendiente" if len(filas) == 1 else "repasos pendientes"
    texto = (f"🔁 <b>Repasos</b>\n\nTienes <b>{len(filas)}</b> {plural}. "
             "Repasar consolida lo que ya estudiaste.")

    # El callback es el mismo que usa el menú: el Agente de Evaluación no
    # distingue si la cápsula llegó por repaso o por navegación.
    botones = [
        [InlineKeyboardButton(text=f"{titulo}  ·  {duracion} min",
                              callback_data=f"m:c:{capsule_id}")]
        for capsule_id, titulo, duracion, _ in filas
    ]
    botones = [
        [InlineKeyboardButton(text=f"{titulo}  ·  {duracion} min",
                              callback_data=f"m:c:{capsule_id}")]
        for capsule_id, titulo, duracion, _ in filas
    ]

    await message.answer(
        texto, reply_markup=InlineKeyboardMarkup(inline_keyboard=botones)
    )

    await message.answer(
        texto, reply_markup=InlineKeyboardMarkup(inline_keyboard=botones)
    )


@router.message(F.text.startswith("🔁 Repasos"))
async def btn_repasos(message: Message):
    await cmd_repasos(message)