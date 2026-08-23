"""Cierre de sesiones de estudio abandonadas.

Una sesión sin `finalizada_en` significa «empezó y no terminó». Si nadie las
cierra, una sesión abierta es ambigua: puede ser un abandono de ayer o alguien
estudiando ahora mismo. Esto las resuelve pasadas unas horas de inactividad.
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Event, Response, StudySession

logger = logging.getLogger(__name__)

INACTIVIDAD_HORAS = 2


async def cerrar_abandonadas(s: AsyncSession) -> int:
    corte = datetime.now(timezone.utc) - timedelta(hours=INACTIVIDAD_HORAS)

    ultima_respuesta = (
        select(
            Response.session_id.label("sid"),
            func.max(Response.respondido_en).label("ultima"),
        )
        .where(Response.session_id.is_not(None))
        .group_by(Response.session_id)
        .subquery()
    )

    filas = (await s.execute(
        select(StudySession, ultima_respuesta.c.ultima)
        .join(ultima_respuesta,
              ultima_respuesta.c.sid == StudySession.id, isouter=True)
        .where(
            StudySession.finalizada_en.is_(None),
            StudySession.iniciada_en < corte,
        )
    )).all()

    cerradas = 0
    for sesion, ultima in filas:
        if ultima is not None and ultima >= corte:
            continue                      # respondió hace poco: sigue estudiando

        # La sesión termina cuando hubo la última señal de vida, no ahora mismo:
        # si no, una sesión abandonada ayer registraría 20 horas de "estudio".
        fin = ultima or sesion.iniciada_en
        sesion.finalizada_en = fin
        sesion.duracion_seg = max(0.0, (fin - sesion.iniciada_en).total_seconds())
        sesion.completada = False

        s.add(Event(
            student_id=sesion.student_id, session_id=sesion.id, ciclo=1,
            tipo="sesion_abandonada",
            payload={"capsule_id": sesion.capsule_id,
                     "duracion_seg": round(sesion.duracion_seg, 1),
                     "con_respuestas": ultima is not None},
        ))
        cerradas += 1

    if cerradas:
        await s.commit()
    return cerradas