"""/menu: navegación de contenido y quiz. Cierra el circuito del Ciclo 1.

Flujo: unidad -> tema -> cápsula -> contenido -> quiz -> responses + mastery.
Solo se muestra lo que el docente dejó activo en el panel.
"""

import logging
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram import F, Router
from aiogram.filters import Command
from app.db.models import ModelPrediction
from app.ml.inferencia import motor as motor_kt
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message,
)
from sqlalchemy import func, select
from app.services import spaced_repetition as sr_service
from app.db.base import SessionLocal
from app.db.models import (
    Capsule, Event, Mastery, Question, Response, Student, StudySession, Topic,
)

logger = logging.getLogger(__name__)
router = Router(name="menu")

UNIDADES = {
    1: "Conceptos básicos",
    2: "Estructuras de programación",
    3: "Vectores y matrices",
    4: "Programación modular",
}

VOLVER = InlineKeyboardButton(text="⬅️ Menú", callback_data="m:inicio")


async def _estudiante(s, tg_id: int) -> Student | None:
    return await s.scalar(select(Student).where(Student.telegram_id == tg_id))


# Telegram no puede descargar de localhost: sus servidores están en internet
# y el backend no. Por eso la imagen se envía como archivo desde disco.
RAIZ_MEDIA = Path(".")


def _archivo_imagen(imagen_url: str | None) -> FSInputFile | None:
    """Convierte la ruta guardada (/media/uploads/x.png) en un archivo enviable."""
    if not imagen_url:
        return None
    ruta = RAIZ_MEDIA / imagen_url.lstrip("/")
    return FSInputFile(ruta) if ruta.is_file() else None


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


@router.callback_query(F.data == "m:quiz")
async def cb_quiz(call: CallbackQuery, state: FSMContext):
    datos = await state.get_data()
    capsule_id = datos.get("capsule_id")
    if not capsule_id:
        await call.answer("Empieza desde /menu.", show_alert=True)
        return

    async with SessionLocal() as s:
        preguntas = list(await s.scalars(
            select(Question)
            .where(Question.capsule_id == capsule_id, Question.activo.is_(True))
            .order_by(Question.id)
        ))

    await state.update_data(
        ids=[p.id for p in preguntas], indice=0, aciertos=0,
        inicio=datetime.now(timezone.utc).timestamp(),
    )
    await _mostrar_pregunta(call, state)


async def _mostrar_pregunta(call: CallbackQuery, state: FSMContext):
    datos = await state.get_data()
    ids, i = datos.get("ids"), datos.get("indice", 0)

    if not ids or i >= len(ids):
        await state.clear()
        await call.answer("Ese quiz ya terminó. Escribe /menu.", show_alert=True)
        return

    async with SessionLocal() as s:
        pregunta = await s.get(Question, ids[i])

    if pregunta is None:                     # el docente la desactivó a mitad
        await state.clear()
        await call.answer("Esa pregunta ya no está disponible. /menu",
                          show_alert=True)
        return

    letras = ["🅐", "🅑", "🅒", "🅓", "🅔", "🅕"]
    botones = [
        [InlineKeyboardButton(text=f"{letras[k]} {op}", callback_data=f"m:r:{k}")]
        for k, op in enumerate(pregunta.opciones)
    ]
    teclado = InlineKeyboardMarkup(inline_keyboard=botones)
    texto = f"<b>Pregunta {i + 1} de {len(ids)}</b>\n\n{pregunta.enunciado}"

    await state.update_data(inicio=datetime.now(timezone.utc).timestamp())

    foto = _archivo_imagen(pregunta.imagen_url)

    if foto is None:
        # Sin imagen: se reescribe el mensaje, como siempre.
        await call.message.edit_text(texto, reply_markup=teclado)
    else:
        if call.message.photo:
            # La anterior también era foto: se reemplaza en el sitio, sin salto.
            await call.message.edit_media(
                InputMediaPhoto(media=foto, caption=texto),
                reply_markup=teclado,
            )
        else:
            # Se viene de un mensaje de texto: Telegram no deja convertirlo en
            # foto. Se envía el nuevo primero para que el chat no quede vacío.
            anterior = call.message
            await call.message.answer_photo(foto, caption=texto,
                                            reply_markup=teclado)
            try:
                await anterior.delete()
            except Exception:
                logger.debug("No se pudo borrar el mensaje anterior", exc_info=True)

    await call.answer()


@router.callback_query(F.data.startswith("m:r:"))
async def cb_responder(call: CallbackQuery, state: FSMContext):
    seleccion = int(call.data.split(":")[2])
    datos = await state.get_data()

    ids, i = datos.get("ids"), datos.get("indice", 0)
    if not ids or i >= len(ids):
        await call.answer("Ese quiz ya terminó. Escribe /menu.", show_alert=True)
        return

    # Bloquea el doble toque: el segundo callback ya no encuentra la marca.
    if datos.get("respondiendo"):
        await call.answer()
        return
    await state.update_data(respondiendo=True)

    tiempo = datetime.now(timezone.utc).timestamp() - datos["inicio"]

    async with SessionLocal() as s:
        est = await _estudiante(s, call.from_user.id)
        pregunta = await s.get(Question, ids[i])
        if est is None or pregunta is None:
            await state.clear()
            await call.answer("No disponible. Escribe /menu.", show_alert=True)
            return

        correcta = seleccion == pregunta.correcta

        # Predicción ANTES de guardar la respuesta: si se hiciera después, el
        # historial ya incluiría el resultado que se está prediciendo.
        probabilidad = await motor_kt.predecir(s, est.id, pregunta.topic_id)

        # orden_interaccion es único por estudiante: la secuencia que usa el SAKT
        ultimo = await s.scalar(
            select(func.max(Response.orden_interaccion))
            .where(Response.student_id == est.id)
        ) or 0

        # cuántas veces ya había respondido ESTA pregunta
        intentos_previos = await s.scalar(
            select(func.count(Response.id)).where(
                Response.student_id == est.id,
                Response.question_id == pregunta.id,
            )
        ) or 0

        s.add(Response(
            student_id=est.id, session_id=datos["session_id"],
            question_id=pregunta.id, topic_id=pregunta.topic_id,
            orden_interaccion=ultimo + 1, intento=intentos_previos + 1,
            seleccion=seleccion, es_correcta=correcta,
            tiempo_seg=round(tiempo, 2),
        ))

        if probabilidad is not None:
            run_id = await motor_kt._resolver_model_run(s)
            if run_id is not None:
                s.add(ModelPrediction(
                    student_id=est.id, model_run_id=run_id,
                    question_id=pregunta.id, topic_id=pregunta.topic_id,
                    secuencia=ultimo + 1,
                    probabilidad=probabilidad,
                    resultado_real=correcta,
                    error_absoluto=abs(probabilidad - (1.0 if correcta else 0.0)),
                ))

        s.add(Event(student_id=est.id, session_id=datos["session_id"], ciclo=1,
                    tipo="pregunta_respondida",
                    payload={"question_id": pregunta.id, "correcta": correcta,
                             "intento": intentos_previos + 1}))
        await s.commit()

        respuesta_texto = escape(pregunta.opciones[pregunta.correcta])
        feedback = escape(pregunta.retroalimentacion) if pregunta.retroalimentacion else None

    aciertos = datos["aciertos"] + (1 if correcta else 0)
    await state.update_data(indice=i + 1, aciertos=aciertos, respondiendo=False)

    cabecera = "✅ <b>Correcto</b>" if correcta else (
        f"❌ <b>Incorrecto</b>\nLa respuesta era: <b>{respuesta_texto}</b>")
    cuerpo = f"\n\n{feedback}" if feedback else ""

    siguiente = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Siguiente ➡️", callback_data="m:sig")
    ]])

    # Si la pregunta tenía imagen, el mensaje es una foto: se edita el pie,
    # no el texto.
    era_foto = call.message.photo is not None

    if i + 1 < len(ids):
        if era_foto:
            await call.message.edit_caption(caption=cabecera + cuerpo,
                                            reply_markup=siguiente)
        else:
            await call.message.edit_text(cabecera + cuerpo, reply_markup=siguiente)
    else:
        await _cerrar_quiz(call, state, cabecera + cuerpo)
    await call.answer()


@router.callback_query(F.data == "m:sig")
async def cb_siguiente(call: CallbackQuery, state: FSMContext):
    await _mostrar_pregunta(call, state)


async def _cerrar_quiz(call: CallbackQuery, state: FSMContext, previo: str):
    datos = await state.get_data()
    total, aciertos = len(datos["ids"]), datos["aciertos"]
    nivel = aciertos / total if total else 0.0

    async with SessionLocal() as s:
        est = await _estudiante(s, call.from_user.id)
        sesion = await s.get(StudySession, datos["session_id"])

        ahora = datetime.now(timezone.utc)
        sesion.finalizada_en = ahora
        sesion.duracion_seg = (ahora - sesion.iniciada_en).total_seconds()
        sesion.completada = True

        # Mastery baseline del Ciclo 1: aciertos / respuestas del tema.
        # En el Ciclo 2 el SAKT lo sobrescribe con fuente='sakt'.
        topic_id = datos["topic_id"]
        agregados = (await s.execute(
            select(func.count(Response.id),
                   func.sum(func.cast(Response.es_correcta, __import__("sqlalchemy").Integer)))
            .where(Response.student_id == est.id, Response.topic_id == topic_id)
        )).one()
        n_total, n_ok = agregados[0] or 0, agregados[1] or 0

        m = await s.scalar(
            select(Mastery).where(Mastery.student_id == est.id,
                                  Mastery.topic_id == topic_id)
        )
        if m is None:
            m = Mastery(student_id=est.id, topic_id=topic_id, fuente="baseline")
            s.add(m)
        m.nivel = (n_ok / n_total) if n_total else 0.0
        m.numero_evidencias = n_total
        m.ultima_respuesta_en = ahora

        # SM-2: programa el próximo repaso de esta cápsula.
        sr, conto = await sr_service.registrar_repaso(
            s, student_id=est.id, topic_id=topic_id,
            capsule_id=datos["capsule_id"],
            calidad=sr_service.calidad_desde_desempeno(nivel),
            session_id=sesion.id,
        )

        s.add(Event(student_id=est.id, session_id=sesion.id, ciclo=1,
                    tipo="capsula_completada",
                    payload={"aciertos": aciertos, "total": total,
                             "nivel_tema": round(m.nivel, 3)}))
        await s.commit()
        intervalo = sr.intervalo_dias
        conto_repaso = conto

    await state.clear()

    marca = "🎉" if nivel >= 0.8 else ("👍" if nivel >= 0.5 else "💪")

    if conto_repaso:
        cuando = "mañana" if intervalo == 1 else f"en {intervalo} días"
        aviso = f"🔁 Te lo recordaré <b>{cuando}</b>."
    else:
        aviso = "🔁 Práctica extra registrada. Tu repaso programado sigue en pie."

    resumen = (f"{previo}\n\n———\n\n{marca} <b>Quiz completado</b>\n"
               f"Aciertos: <b>{aciertos} de {total}</b> ({nivel:.0%})\n\n"
               f"{aviso}")
    volver = InlineKeyboardMarkup(inline_keyboard=[[VOLVER]])

    if call.message.photo:
        await call.message.edit_caption(caption=resumen, reply_markup=volver)
    else:
        await call.message.edit_text(resumen, reply_markup=volver)