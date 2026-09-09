"""Generación y envío de recordatorios de repaso. [Agente de Repetición Espaciada]

Dos fases separadas a propósito:
  · generar_pendientes: crea filas en `reminders` a partir de spaced_repetition
  · enviar_pendientes : las manda por Telegram y registra el resultado

Así queda constancia de lo programado aunque el envío falle, y el reintento no
recalcula nada.
"""

import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Capsule, Event, Reminder, SpacedRepetition, Student

logger = logging.getLogger(__name__)

HORA_INICIO = 8       # no se molesta antes de las 08:00 locales
HORA_FIN = 21         # ni después de las 21:00
MAX_INTENTOS = 3
ADELANTO_HORAS = 12   # genera con antelación lo que vence pronto
LOTE = 50


def _ajustar_a_horario_decente(momento: datetime) -> datetime:
    """Mueve el envío a una franja razonable en la zona horaria del estudio.

    Un mensaje a las 3 de la madrugada no es un recordatorio: es una razón para
    silenciar el bot. Y en un estudio con consentimiento, para abandonarlo.
    """
    tz = ZoneInfo(settings.TIMEZONE)
    local = momento.astimezone(tz)

    if local.hour < HORA_INICIO:
        local = local.replace(hour=HORA_INICIO, minute=0, second=0, microsecond=0)
    elif local.hour >= HORA_FIN:
        local = (local + timedelta(days=1)).replace(
            hour=HORA_INICIO, minute=0, second=0, microsecond=0)

    return local.astimezone(timezone.utc)


async def generar_pendientes(s: AsyncSession) -> int:
    limite = datetime.now(timezone.utc) + timedelta(hours=ADELANTO_HORAS)

    filas = (await s.execute(
        select(SpacedRepetition, Capsule)
        .join(Capsule, Capsule.id == SpacedRepetition.capsule_id)
        .join(Student, Student.id == SpacedRepetition.student_id)
        .where(
            SpacedRepetition.activo.is_(True),
            SpacedRepetition.proxima_revision_en.is_not(None),
            SpacedRepetition.proxima_revision_en <= limite,
            Capsule.activo.is_(True),
            Student.activo.is_(True),
            Student.consentimiento.is_(True),
        )
    )).all()

    creados = 0
    for sr, capsula in filas:
        programado = _ajustar_a_horario_decente(sr.proxima_revision_en)

        # `programado` es determinista, así que esto evita duplicados aunque el
        # planificador corra cada cinco minutos.
        ya_existe = await s.scalar(
            select(Reminder.id).where(
                Reminder.spaced_repetition_id == sr.id,
                Reminder.programado_en == programado,
            )
        )
        if ya_existe:
            continue

        s.add(Reminder(
            student_id=sr.student_id,
            spaced_repetition_id=sr.id,
            titulo=f"Repaso: {capsula.titulo}"[:200],
            mensaje=(
                f"🔁 <b>Toca repasar</b>\n\n"
                f"{capsula.titulo}\n"
                f"<i>{capsula.duracion_min} min</i>\n\n"
                f"Repasar ahora consolida lo que ya estudiaste."
            ),
            canal="telegram",
            programado_en=programado,
            estado="pendiente",
            intentos_envio=0,
        ))
        creados += 1

    if creados:
        await s.commit()
    return creados


async def enviar_pendientes(bot: Bot, s: AsyncSession) -> int:
    """Envía un solo mensaje por estudiante, no uno por cápsula vencida.

    Alguien con cuatro repasos pendientes recibiría cuatro mensajes seguidos,
    que es la vía más rápida a que silencie el bot. Las filas de `reminders` se
    siguen creando una por cápsula —son el registro de lo programado— pero
    todas las de un mismo estudiante se marcan como enviadas con un único aviso
    que lo lleva a la lista de repasos.
    """
    ahora = datetime.now(timezone.utc)

    filas = (await s.execute(
        select(Reminder, Student, SpacedRepetition)
        .join(Student, Student.id == Reminder.student_id)
        .join(SpacedRepetition,
              SpacedRepetition.id == Reminder.spaced_repetition_id)
        .where(
            Reminder.estado == "pendiente",
            Reminder.programado_en <= ahora,
            Student.activo.is_(True),
            Student.consentimiento.is_(True),
        )
        .order_by(Reminder.student_id, Reminder.programado_en)
        .limit(LOTE)
    )).all()

    # Agrupa por estudiante: un aviso por persona, con todas sus cápsulas.
    por_estudiante: dict[int, list] = {}
    estudiantes: dict[int, Student] = {}
    for recordatorio, estudiante, sr in filas:
        por_estudiante.setdefault(estudiante.id, []).append((recordatorio, sr))
        estudiantes[estudiante.id] = estudiante

    enviados = 0
    for student_id, pendientes in por_estudiante.items():
        estudiante = estudiantes[student_id]
        n = len(pendientes)

        plural = "repaso pendiente" if n == 1 else "repasos pendientes"
        mensaje = (f"🔁 <b>Toca repasar</b>\n\n"
                   f"Tienes <b>{n}</b> {plural}.\n"
                   f"Repasar ahora consolida lo que ya estudiaste.")

        # Con una sola cápsula se entra directo; con varias, a la lista.
        if n == 1:
            destino = f"m:c:{pendientes[0][1].capsule_id}"
            etiqueta = "📖 Repasar ahora"
        else:
            destino = "m:repasos"
            etiqueta = f"📋 Ver mis {n} repasos"

        teclado = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=etiqueta, callback_data=destino)
        ]])

        try:
            await bot.send_message(estudiante.telegram_id, mensaje,
                                   reply_markup=teclado)
            ahora_env = datetime.now(timezone.utc)
            for recordatorio, sr in pendientes:
                recordatorio.estado = "enviado"
                recordatorio.enviado_en = ahora_env
                recordatorio.intentos_envio += 1
            s.add(Event(student_id=student_id, ciclo=1,
                        tipo="recordatorio_enviado",
                        payload={"n_capsulas": n,
                                 "reminder_ids": [r.id for r, _ in pendientes]}))
            enviados += 1
        except Exception as e:                       # noqa: BLE001
            for recordatorio, _ in pendientes:
                recordatorio.intentos_envio += 1
                recordatorio.error_detalle = str(e)[:500]
                if recordatorio.intentos_envio >= MAX_INTENTOS:
                    recordatorio.estado = "fallido"
            s.add(Event(student_id=student_id, ciclo=1,
                        tipo="recordatorio_fallido",
                        payload={"n_capsulas": n, "error": str(e)[:200]}))
            logger.warning("Fallo al enviar recordatorio a %s: %s",
                           student_id, e)

    if filas:
        await s.commit()
    return enviados