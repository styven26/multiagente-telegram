"""Piezas compartidas entre los agentes que hablan por Telegram."""

import logging
import time
from contextlib import asynccontextmanager
from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy import select
from aiogram.fsm.context import FSMContext

from app.db.models import AgentInteraction, Student

logger = logging.getLogger(__name__)

# El callback lo atiende el Orquestador, pero varios agentes lo ofrecen.
VOLVER = InlineKeyboardButton(text="⬅️ Menú", callback_data="m:inicio")


async def estudiante_por_telegram(s, tg_id: int) -> Student | None:
    return await s.scalar(select(Student).where(Student.telegram_id == tg_id))


@asynccontextmanager
async def traza(s, agente: str, accion: str, *, student_id: int | None = None,
                session_id: int | None = None, entrada: dict | None = None):
    """Registra la actuación de un agente en agent_interactions.

    Es la evidencia empírica de la coordinación entre agentes: sin esta traza,
    la arquitectura multi-agente solo existe en el diagrama. Solo se instrumentan
    los traspasos entre agentes, no las operaciones internas — registrar todo
    llenaría la tabla de ruido y ocultaría justo la secuencia que interesa.

    Uso:
        async with traza(s, "evaluation", "calificar", student_id=est.id) as t:
            ...trabajo del agente...
            t["salida"] = {...}
    """
    inicio = time.perf_counter()
    caja: dict = {"salida": None}
    exitosa, error = True, None
    try:
        yield caja
    except Exception as e:                           # noqa: BLE001
        exitosa, error = False, repr(e)[:500]
        raise
    finally:
        s.add(AgentInteraction(
            student_id=student_id, session_id=session_id,
            agente=agente, accion=accion,
            entrada=entrada, salida=caja["salida"],
            exitosa=exitosa, error=error,
            duracion_ms=round((time.perf_counter() - inicio) * 1000, 2),
        ))


async def teclado_principal(s, student_id: int) -> ReplyKeyboardMarkup:
    """Menú fijo inferior. El número de repasos se calcula al enviarlo, así que
    hay que reenviar el teclado cuando esa cifra cambia — al cerrar un quiz."""
    from app.agents.orchestrator.handlers.repasos import contar_pendientes

    n = await contar_pendientes(s, student_id)

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Estudiar"),
             KeyboardButton(text=f"🔁 Repasos ({n})")],
            [KeyboardButton(text="👤 Perfil"),
             KeyboardButton(text="🚪 Salir")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


async def limpiar_navegacion(message, state: FSMContext) -> None:
    """Borra el mensaje de navegación que quedó abierto.

    Los teclados inline de Telegram no caducan: si el estudiante deja el menú
    de temas arriba y se va al perfil, esos botones siguen activos y puede
    volver a una pantalla que ya no corresponde al estado actual.
    """
    datos = await state.get_data()
    msg_id = datos.get("nav_msg_id")
    if msg_id is None:
        return
    try:
        await message.bot.delete_message(message.chat.id, msg_id)
    except Exception:                                # noqa: BLE001
        pass                                         # ya lo borró el usuario
    await state.update_data(nav_msg_id=None)