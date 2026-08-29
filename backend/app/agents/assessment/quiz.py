"""Agente de Evaluación: entrega el quiz, califica y alimenta el modelo
del estudiante. [MVP — Ciclo 1]

Recibe el control del Orquestador cuando el estudiante pulsa "Hacer el quiz"
y se lo devuelve al terminar. Cada respuesta produce tres efectos: la fila en
`responses`, la predicción del modelo en `model_predictions`, y —al cerrar—
la actualización del dominio y la programación del repaso.
"""

import logging
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto,
)
from sqlalchemy import Integer, func, select

from app.agents.base import VOLVER, estudiante_por_telegram as _estudiante
from app.agents.spaced_repetition import sm2 as sr_service
from app.agents.student_model.inferencia import motor as motor_kt
from app.db.base import SessionLocal
from app.db.models import (
    Event, Mastery, ModelPrediction, Question, Response, StudySession,
)

logger = logging.getLogger(__name__)
router = Router(name="assessment")

LETRAS = ["🅐", "🅑", "🅒", "🅓", "🅔", "🅕"]

# Telegram no puede descargar de localhost: sus servidores están en internet
# y el backend no. Por eso la imagen se envía como archivo desde disco.
RAIZ_MEDIA = Path(".")


def _archivo_imagen(imagen_url: str | None) -> FSInputFile | None:
    """Convierte la ruta guardada (/media/uploads/x.png) en un archivo enviable."""
    if not imagen_url:
        return None
    ruta = RAIZ_MEDIA / imagen_url.lstrip("/")
    return FSInputFile(ruta) if ruta.is_file() else None


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

    # Las opciones van en el texto, no en los botones: Telegram corta el
    # texto de un botón que no cabe, y en móvil eso las deja ilegibles.
    opciones_texto = "\n".join(
        f"{LETRAS[k]} {escape(op)}" for k, op in enumerate(pregunta.opciones)
    )
    texto = (f"<b>Pregunta {i + 1} de {len(ids)}</b>\n\n"
             f"{pregunta.enunciado}\n\n{opciones_texto}")

    # Una sola fila con las letras: caben todas en el ancho del móvil.
    teclado = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=LETRAS[k], callback_data=f"m:r:{k}")
        for k in range(len(pregunta.opciones))
    ]])

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
                   func.sum(func.cast(Response.es_correcta, Integer)))
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