"""/start: alta del estudiante y consentimiento informado. [Ciclo 1]"""

from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message,
)
from sqlalchemy import select

from app.core.anonymization import generar_codigo_anonimo
from app.db.base import SessionLocal
from app.db.models import Event, Student

router = Router(name="start")

VERSION_CONSENTIMIENTO = "v1.1"

TEXTO_CONSENTIMIENTO = (
    "👋 <b>Bienvenido/a</b>\n\n"
    "Este es un tutor de <b>Fundamentos de Programación</b> que forma parte "
    "de un proyecto de investigación académica.\n\n"
    "<b>Qué implica participar:</b>\n"
    "• Recibirás micro-cápsulas breves y cuestionarios cortos.\n"
    "• Se registrarán tus respuestas y tiempos de estudio.\n"
    "• Tus datos se analizan de forma <b>anónima</b>: se te asigna un código y "
    "tu identidad no aparece en los resultados.\n"
    "• La participación es <b>voluntaria</b> y puedes retirarte cuando quieras "
    "con el comando /salir.\n"
    "• <b>No participar no afecta de ninguna manera tu calificación</b> en la "
    "asignatura.\n\n"
    "¿Aceptas participar?"
)

teclado_consentimiento = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="✅ Acepto", callback_data="consent:si"),
    InlineKeyboardButton(text="❌ No acepto", callback_data="consent:no"),
]])


@router.message(CommandStart())
async def cmd_start(message: Message):
    tg_id = message.from_user.id

    async with SessionLocal() as s:
        student = await s.scalar(select(Student).where(Student.telegram_id == tg_id))
        es_nuevo = student is None

        if es_nuevo:
            student = Student(
                telegram_id=tg_id,
                codigo_anonimo=generar_codigo_anonimo(tg_id),
                nombre_telegram=(message.from_user.full_name or "")[:128],
                consentimiento=False,
                activo=True,
            )
            s.add(student)
            await s.flush()

        # Quien se retiró y vuelve con /start se reactiva.
        reactivado = False
        if not es_nuevo and student.consentimiento and not student.activo:
            student.activo = True
            reactivado = True
            s.add(Event(student_id=student.id, ciclo=1, tipo="reingreso_estudio"))

        s.add(Event(student_id=student.id, ciclo=1, tipo="inicio",
                    payload={"comando": "/start", "nuevo": es_nuevo}))
        ya_acepto = student.consentimiento
        codigo = student.codigo_anonimo
        await s.commit()

    if ya_acepto:
        saludo = ("👋 Bienvenido/a de vuelta.\n\n" if reactivado
                  else "Ya estás registrado/a. ")
        await message.answer(
            f"{saludo}Tu código es <code>{codigo}</code>.\n"
            "Usa /menu para continuar."
        )
    else:
        await message.answer(TEXTO_CONSENTIMIENTO, reply_markup=teclado_consentimiento)


@router.callback_query(F.data.startswith("consent:"))
async def cb_consentimiento(callback: CallbackQuery):
    acepta = callback.data.split(":")[1] == "si"
    tg_id = callback.from_user.id

    async with SessionLocal() as s:
        student = await s.scalar(select(Student).where(Student.telegram_id == tg_id))
        if student is None:
            await callback.answer("Usa /start primero.", show_alert=True)
            return

        if acepta:
            student.consentimiento = True
            student.fecha_consentimiento = datetime.now(timezone.utc)
            student.version_consentimiento = VERSION_CONSENTIMIENTO
            student.activo = True          # revierte un rechazo anterior
        else:
            student.activo = False

        s.add(Event(student_id=student.id, ciclo=1, tipo="consentimiento",
                    payload={"acepta": acepta, "version": VERSION_CONSENTIMIENTO}))
        codigo = student.codigo_anonimo
        await s.commit()

    if acepta:
        texto = (
            f"✅ Gracias por participar.\n\n"
            f"Tu código anónimo es <code>{codigo}</code>.\n\n"
            "Usa /menu para ver los temas disponibles."
        )
    else:
        texto = (
            "Entendido, no se registrarán tus datos de estudio.\n"
            "Si cambias de opinión, escribe /start."
        )

    await callback.message.edit_text(texto)
    await callback.answer()