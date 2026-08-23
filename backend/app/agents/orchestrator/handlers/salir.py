"""/salir: retiro voluntario del estudio. [Protocolo CEISH]

No se borran los registros históricos: se marca activo=False y el bot deja de
enviar contenido. El borrado, si el comité lo exige, se hace al cerrar el estudio.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message,
)
from sqlalchemy import select

from app.db.base import SessionLocal
from app.db.models import Event, Student

router = Router(name="salir")

teclado_salir = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="Sí, retirarme", callback_data="salir:si"),
    InlineKeyboardButton(text="Cancelar", callback_data="salir:no"),
]])


@router.message(Command("salir"))
async def cmd_salir(message: Message):
    await message.answer(
        "¿Seguro que quieres retirarte del estudio?\n\n"
        "Dejarás de recibir cápsulas y recordatorios. Tu participación es "
        "voluntaria.",
        reply_markup=teclado_salir,
    )


@router.callback_query(F.data.startswith("salir:"))
async def cb_salir(callback: CallbackQuery):
    if callback.data.endswith(":no"):
        await callback.message.edit_text("Perfecto, sigues participando. /menu")
        await callback.answer()
        return

    async with SessionLocal() as s:
        student = await s.scalar(
            select(Student).where(Student.telegram_id == callback.from_user.id)
        )
        if student is not None:
            student.activo = False
            s.add(Event(student_id=student.id, ciclo=1, tipo="retiro_estudio"))
            await s.commit()

    await callback.message.edit_text(
        "Te has retirado del estudio. Gracias por el tiempo que dedicaste.\n\n"
        "Si quieres volver, escribe /start."
    )
    await callback.answer()