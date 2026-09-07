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
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")            # sin ventana: el servidor no tiene pantalla
import matplotlib.pyplot as plt  # noqa: E402

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from sqlalchemy import Integer, func, select

from app.config import settings
from app.db.base import SessionLocal
from app.db.models import (
    Capsule, Mastery, Response, SpacedRepetition, Student, StudySession, Topic,
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

    alto = max(2.0, 0.6 * len(nombres) + 1.0)
    fig, ax = plt.subplots(figsize=(7, alto), dpi=130)

    barras = ax.barh(nombres, niveles,
                     color=[_color(n) for n in niveles], height=0.55)

    for barra, nivel in zip(barras, niveles):
        ax.text(min(nivel + 0.02, 0.97), barra.get_y() + barra.get_height() / 2,
                f"{nivel:.0%}", va="center", fontsize=10, color="#1a1830")

    ax.set_xlim(0, 1.05)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=9)
    ax.tick_params(axis="y", labelsize=10, length=0)
    ax.set_title("Tu dominio por tema", fontsize=12, pad=12, loc="left")

    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color("#d5d3cc")
    ax.grid(axis="x", color="#e8e6df", linewidth=0.8)
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

        proximo = await s.scalar(
            select(func.min(SpacedRepetition.proxima_revision_en))
            .where(SpacedRepetition.student_id == est.id,
                   SpacedRepetition.activo.is_(True))
        )

    acierto = (n_ok / n_resp) if n_resp else 0.0

    lineas = [
        "👤 <b>Tu perfil</b>",
        f"Código: <code>{est.codigo_anonimo}</code>",
        "",
        "📊 <b>Rendimiento</b>",
        f"Cápsulas completadas: <b>{completadas}</b> de {disponibles}",
        f"Respuestas correctas: <b>{int(n_ok)}</b>",
        f"Respuestas incorrectas: <b>{n_resp - int(n_ok)}</b>",
        f"Tasa de acierto: <b>{acierto:.0%}</b>",
    ]

    if proximo is not None:
        local = proximo.astimezone(ZoneInfo(settings.TIMEZONE))
        lineas += ["", f"🔁 Próximo repaso: <b>{local:%d/%m a las %H:%M}</b>"]

    texto = "\n".join(lineas)

    if not filas:
        await message.answer(
            texto + "\n\n<i>Completa una cápsula para ver tu dominio por tema.</i>"
        )
        return

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