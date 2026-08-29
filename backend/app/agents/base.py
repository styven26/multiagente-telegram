"""Piezas compartidas entre los agentes que hablan por Telegram."""

from aiogram.types import InlineKeyboardButton
from sqlalchemy import select

from app.db.models import Student

# El callback lo atiende el Orquestador, pero varios agentes lo ofrecen.
VOLVER = InlineKeyboardButton(text="⬅️ Menú", callback_data="m:inicio")


async def estudiante_por_telegram(s, tg_id: int) -> Student | None:
    return await s.scalar(select(Student).where(Student.telegram_id == tg_id))