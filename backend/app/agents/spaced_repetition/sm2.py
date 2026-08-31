"""Agente de Repetición Espaciada — SM-2 clásico. [Se adelanta al Ciclo 1]

Se implementa desde ahora, aunque el cronograma lo ubique en el Ciclo 3, porque
los intervalos son de días: la red neuronal del Ciclo 3 necesita meses de
historial real de repasos para poder entrenarse con algo.

SM-2 (Piotr Woźniak, 1987):
    q < 3   -> se falló: repeticiones a 0, intervalo a 1 día
    q >= 3  -> 1er repaso: 1 día | 2do: 6 días | resto: intervalo * ease_factor
    EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02)),  mínimo 1.3

`ajuste_red_neuronal` multiplica el intervalo final. En el Ciclo 1 vale 1.0 y no
cambia nada; en el Ciclo 3 la red escribirá ahí su factor por estudiante.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import traza
from app.db.models import Event, SpacedRepetition

EF_MINIMO = 1.3
INTERVALO_MAX_DIAS = 30


def calidad_desde_desempeno(proporcion_aciertos: float) -> int:
    """Traduce el resultado del quiz (0-1) a la escala SM-2 (0-5).

    Los cortes son una decisión de diseño, no parte de SM-2: documéntalos igual
    en la tesis, porque cambiarlos altera todos los intervalos.
    """
    if proporcion_aciertos >= 1.0:
        return 5
    if proporcion_aciertos >= 0.8:
        return 4
    if proporcion_aciertos >= 0.6:
        return 3
    if proporcion_aciertos >= 0.4:
        return 2
    if proporcion_aciertos >= 0.2:
        return 1
    return 0


async def registrar_repaso(s: AsyncSession, student_id: int, topic_id: str,
                            capsule_id: str, calidad: int,
                            session_id: int | None = None) -> tuple[SpacedRepetition, bool]:
    ahora = datetime.now(timezone.utc)

    sr = await s.scalar(
        select(SpacedRepetition).where(
            SpacedRepetition.student_id == student_id,
            SpacedRepetition.capsule_id == capsule_id,
        )
    )
    if sr is None:
        # Los `default=` de SQLAlchemy se aplican en el INSERT, no al construir
        # el objeto: hay que dar los valores iniciales aquí o serían None.
        sr = SpacedRepetition(
            student_id=student_id, topic_id=topic_id, capsule_id=capsule_id,
            calidad=0, ease_factor=2.5, intervalo_dias=0, repeticiones=0,
            errores=0, dificultad=0.5, estabilidad=0.0,
            ajuste_red_neuronal=1.0, activo=True,
        )
        s.add(sr)
    
    async with traza(s, "spaced_repetition", "programar_repaso",
                     student_id=student_id, session_id=session_id,
                     entrada={"capsule_id": capsule_id, "calidad": calidad}) as t:

        # --- Guardián: repaso adelantado = práctica extra, no avanza ---
        if sr.proxima_revision_en is not None and ahora < sr.proxima_revision_en:
            s.add(Event(
                student_id=student_id, session_id=session_id, ciclo=1,
                tipo="practica_extra",
                payload={"capsule_id": capsule_id, "calidad": calidad,
                         "programado_para": sr.proxima_revision_en.isoformat()},
            ))
            t["salida"] = {"conto": False, "motivo": "repaso_adelantado"}
            return sr, False

        # --- Ease factor ---
        delta = 0.1 - (5 - calidad) * (0.08 + (5 - calidad) * 0.02)
        sr.ease_factor = max(EF_MINIMO, sr.ease_factor + delta)

        # --- Intervalo y repeticiones ---
        if calidad < 3:
            sr.repeticiones = 0
            sr.errores += 1
            intervalo = 1
        else:
            if sr.repeticiones == 0:
                intervalo = 1
            elif sr.repeticiones == 1:
                intervalo = 6
            else:
                intervalo = round(sr.intervalo_dias * sr.ease_factor)
            sr.repeticiones += 1

        intervalo = max(1, round(intervalo * sr.ajuste_red_neuronal))
        intervalo = min(intervalo, INTERVALO_MAX_DIAS)

        sr.calidad = calidad
        sr.intervalo_dias = intervalo
        # Dificultad normalizada 0-1 (0 = fácil, 1 = difícil). El EF puede subir
        # por encima de 2.5, así que se acota: ck_spaced_difficulty exige ese rango.
        sr.dificultad = round(min(1.0, max(0.0, (2.5 - sr.ease_factor) / 2.4 + 0.5)), 4)
        sr.estabilidad = float(intervalo)
        sr.ultima_revision_en = ahora
        sr.proxima_revision_en = ahora + timedelta(days=intervalo)
        sr.activo = True

        s.add(Event(
            student_id=student_id, session_id=session_id, ciclo=1,
            tipo="repaso_programado",
            payload={"capsule_id": capsule_id, "calidad": calidad,
                     "intervalo_dias": intervalo,
                     "ease_factor": round(sr.ease_factor, 3)},
        ))

        t["salida"] = {"conto": True, "intervalo_dias": intervalo,
                       "repeticiones": sr.repeticiones,
                       "ease_factor": round(sr.ease_factor, 3)}
        return sr, True