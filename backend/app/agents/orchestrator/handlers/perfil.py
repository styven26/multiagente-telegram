"""/perfil: resumen de avance del estudiante. [Ciclo 1]

Presenta al estudiante los datos que el sistema ya tiene sobre él: cápsulas
completadas, desempeño y dominio por tema. No muestra nombre ni correo — el
estudio es anónimo y el estudiante solo se identifica por su código.

El Agente Orquestador consulta y presenta; los datos provienen del Agente de
Evaluación (responses) y del Agente de Modelado del Estudiante (mastery).
"""

import logging
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")            # sin ventana: el servidor no tiene pantalla
import matplotlib.pyplot as plt  # noqa: E402

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from sqlalchemy import Integer, func, select
from aiogram.fsm.context import FSMContext
from app.agents.base import limpiar_navegacion

from app.db.base import SessionLocal
from app.db.models import (
    Capsule, Mastery, Response, Student, StudySession, Topic,
)

logger = logging.getLogger(__name__)
router = Router(name="perfil")

# Mismos cortes que usa el dashboard docente: verde domina, ámbar en proceso,
# rojo necesita repaso. Cambiarlos aquí los desalinea del panel.
DOMINIO_ALTO = 0.8
DOMINIO_MEDIO = 0.5


def _color(nivel: float) -> str:
    if nivel >= DOMINIO_ALTO:
        return "#3aa17e"
    if nivel >= DOMINIO_MEDIO:
        return "#e0a030"
    return "#c0392b"


def _grafico(filas) -> Path:
    """Barras horizontales del dominio por tema. Devuelve la ruta del PNG."""
    nombres = [f[0] for f in filas][::-1]
    niveles = [f[1] for f in filas][::-1]

    alto = max(1.4, 0.42 * len(nombres) + 0.6)
    fig, ax = plt.subplots(figsize=(5, alto), dpi=110)

    barras = ax.barh(nombres, niveles,
                     color=[_color(n) for n in niveles], height=0.5)

    for barra, nivel in zip(barras, niveles):
        ax.text(min(nivel + 0.02, 0.96), barra.get_y() + barra.get_height() / 2,
                f"{nivel:.0%}", va="center", fontsize=8, color="#1a1830")

    ax.set_xlim(0, 1.05)
    ax.set_xticks([0, 0.5, 1.0])
    ax.set_xticklabels(["0%", "50%", "100%"], fontsize=7.5)
    ax.tick_params(axis="y", labelsize=8, length=0)
    ax.set_title("Dominio por tema", fontsize=10, pad=8, loc="left", color="#1a1830")

    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color("#d5d3cc")
    ax.grid(axis="x", color="#e8e6df", linewidth=0.7)
    ax.set_axisbelow(True)

    fig.tight_layout()

    ruta = Path(tempfile.gettempdir()) / f"perfil_{id(fig)}.png"
    fig.savefig(ruta, bbox_inches="tight", facecolor="white")
    plt.close(fig)            # sin esto las figuras se acumulan en memoria
    return ruta


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
            select(Topic.nombre, Mastery.nivel)
            .join(Mastery, Mastery.topic_id == Topic.id)
            .where(Mastery.student_id == est.id)
            .order_by(Topic.orden)
        )).all()

    acierto = (n_ok / n_resp) if n_resp else 0.0

    texto = "\n".join([
        "👤 <b>Tu perfil</b>",
        f"Código: <code>{est.codigo_anonimo}</code>",
        "",
        "📊 <b>Rendimiento</b>",
        f"Cápsulas completadas: <b>{completadas}</b> de {disponibles}",
        f"Respuestas correctas: <b>{int(n_ok)}</b>",
        f"Respuestas incorrectas: <b>{n_resp - int(n_ok)}</b>",
        f"Tasa de acierto: <b>{acierto:.0%}</b>",
    ])

    if not filas:
        await message.answer(
            texto + "\n\n<i>Completa una cápsula para ver tu dominio por tema.</i>"
        )
        return

    # Un solo mensaje: la imagen arriba y el rendimiento como pie de foto.
    ruta = None
    try:
        ruta = _grafico(filas)
        await message.answer_photo(FSInputFile(ruta), caption=texto)
    except Exception:                                # noqa: BLE001
        # Si el gráfico falla, el estudiante igual recibe sus datos.
        logger.exception("No se pudo generar el gráfico del perfil")
        await message.answer(texto)
    finally:
        if ruta is not None:
            ruta.unlink(missing_ok=True)


@router.message(F.text.startswith("👤 Perfil"))
async def btn_perfil(message: Message, state: FSMContext):
    await limpiar_navegacion(message, state)
    await cmd_perfil(message)
