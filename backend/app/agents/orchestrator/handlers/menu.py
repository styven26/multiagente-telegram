"""/menu: navegación del contenido. [Agente Orquestador — Ciclo 1]

Flujo: unidad -> tema -> cápsula -> contenido. Al pulsar "Hacer el quiz" el
control pasa al Agente de Evaluación (app/agents/assessment/quiz.py), que lo
devuelve aquí al terminar mediante el botón Menú.

Solo se muestra lo que el docente dejó activo en el panel.
"""

from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message,
)
from sqlalchemy import func, select

from app.agents.base import VOLVER, estudiante_por_telegram as _estudiante
from app.db.base import SessionLocal
from app.db.models import Capsule, Event, Question, StudySession, Topic

router = Router(name="menu")

UNIDADES = {
    1: "Conceptos básicos",
    2: "Estructuras de programación",
    3: "Vectores y matrices",
    4: "Programación modular",
}


async def _menu_unidades(s) -> tuple[str, InlineKeyboardMarkup]:
    """Solo unidades que tengan al menos un tema activo."""
    filas = await s.execute(
        select(Topic.unidad, func.count(Topic.id))
        .where(Topic.activo.is_(True), Topic.unidad.is_not(None))
        .group_by(Topic.unidad)
    )
    conteo = {u: n for u, n in filas.all()}

    botones = [
        [InlineKeyboardButton(
            text=f"{n}. {nombre}  ({conteo[n]})", callback_data=f"m:u:{n}")]
        for n, nombre in UNIDADES.items() if conteo.get(n)
    ]

    if not botones:
        return ("Todavía no hay contenido disponible. Vuelve pronto.",
                InlineKeyboardMarkup(inline_keyboard=[]))

    return ("📚 <b>Fundamentos de Programación</b>\n\nElige una unidad:",
            InlineKeyboardMarkup(inline_keyboard=botones))


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    async with SessionLocal() as s:
        est = await _estudiante(s, message.from_user.id)
        if est is None or not est.consentimiento:
            await message.answer("Primero necesito tu registro. Escribe /start.")
            return
        if not est.activo:
            await message.answer("Te retiraste del estudio. Escribe /start para volver.")
            return
        texto, teclado = await _menu_unidades(s)
    await message.answer(texto, reply_markup=teclado)


@router.callback_query(F.data == "m:inicio")
async def cb_inicio(call: CallbackQuery, state: FSMContext):
    await state.clear()
    async with SessionLocal() as s:
        texto, teclado = await _menu_unidades(s)

    # Si el quiz terminó en una pregunta con imagen, el mensaje es una foto:
    # no se puede convertir en texto, hay que reemplazarlo.
    if call.message.photo:
        await call.message.delete()
        await call.message.answer(texto, reply_markup=teclado)
    else:
        await call.message.edit_text(texto, reply_markup=teclado)

    await call.answer()


@router.callback_query(F.data.startswith("m:u:"))
async def cb_unidad(call: CallbackQuery):
    numero = int(call.data.split(":")[2])

    async with SessionLocal() as s:
        temas = list(await s.scalars(
            select(Topic)
            .where(Topic.activo.is_(True), Topic.unidad == numero)
            .order_by(Topic.orden)
        ))

    botones = [
        [InlineKeyboardButton(text=f"{t.emoji or '•'} {t.nombre}",
                              callback_data=f"m:t:{t.id}")]
        for t in temas
    ]
    botones.append([VOLVER])

    await call.message.edit_text(
        f"<b>Unidad {numero} · {UNIDADES[numero]}</b>\n\nElige un tema:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=botones),
    )
    await call.answer()


@router.callback_query(F.data.startswith("m:t:"))
async def cb_tema(call: CallbackQuery):
    topic_id = call.data.split(":", 2)[2]

    async with SessionLocal() as s:
        tema = await s.get(Topic, topic_id)
        capsulas = list(await s.scalars(
            select(Capsule)
            .where(Capsule.topic_id == topic_id, Capsule.activo.is_(True))
            .order_by(Capsule.orden)
        ))

    if not capsulas:
        await call.answer("Este tema todavía no tiene contenido.", show_alert=True)
        return

    botones = [
        [InlineKeyboardButton(text=f"{c.orden}. {c.titulo}  ·  {c.duracion_min} min",
                              callback_data=f"m:c:{c.id}")]
        for c in capsulas
    ]
    botones.append([InlineKeyboardButton(
        text="⬅️ Unidad", callback_data=f"m:u:{tema.unidad}")])

    await call.message.edit_text(
        f"{tema.emoji or ''} <b>{escape(tema.nombre)}</b>\n\nElige una micro-cápsula:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=botones),
    )
    await call.answer()


@router.callback_query(F.data.startswith("m:c:"))
async def cb_capsula(call: CallbackQuery, state: FSMContext):
    capsule_id = call.data.split(":", 2)[2]

    async with SessionLocal() as s:
        est = await _estudiante(s, call.from_user.id)
        capsula = await s.get(Capsule, capsule_id)
        if est is None or capsula is None:
            await call.answer("No disponible.", show_alert=True)
            return

        # Reutiliza la sesión abierta si vuelve a la misma cápsula sin terminarla.
        sesion = await s.scalar(
            select(StudySession).where(
                StudySession.student_id == est.id,
                StudySession.capsule_id == capsule_id,
                StudySession.finalizada_en.is_(None),
            ).order_by(StudySession.iniciada_en.desc())
        )

        if sesion is None:
            sesion = StudySession(
                student_id=est.id, capsule_id=capsule_id,
                ciclo=1, estrategia="fija", completada=False,
            )
            s.add(sesion)
            await s.flush()

        s.add(Event(student_id=est.id, session_id=sesion.id, ciclo=1,
                    tipo="capsula_abierta", payload={"capsule_id": capsule_id}))
        await s.commit()

        session_id = sesion.id
        n_preguntas = await s.scalar(
            select(func.count(Question.id)).where(
                Question.capsule_id == capsule_id, Question.activo.is_(True))
        )
        texto = (f"📖 <b>{escape(capsula.titulo)}</b>\n\n{capsula.contenido}\n\n"
                 f"<i>🎯 {escape(capsula.objetivo)}</i>")

    await state.update_data(session_id=session_id, capsule_id=capsule_id,
                            topic_id=capsula.topic_id)

    # El callback "m:quiz" lo atiende el Agente de Evaluación.
    if n_preguntas:
        teclado = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=f"✏️ Hacer el quiz ({n_preguntas})",
                                 callback_data="m:quiz")
        ], [VOLVER]])
    else:
        teclado = InlineKeyboardMarkup(inline_keyboard=[[VOLVER]])
        texto += "\n\n<i>Esta cápsula aún no tiene preguntas.</i>"

    if call.message.photo:
        await call.message.delete()
        await call.message.answer(texto, reply_markup=teclado)
    else:
        await call.message.edit_text(texto, reply_markup=teclado)
    await call.answer()