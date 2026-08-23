"""Métricas del dashboard. [Ciclo 1 - Lean]

DEFINICIONES (fíjalas aquí y cítalas igual en la tesis):
  · Estudiante registrado : consentimiento = TRUE
  · Estudiante activo     : respondió al menos una pregunta en los últimos 7 días
  · Cápsula entregada     : StudySession con completada = TRUE
  · Tasa de acierto       : aciertos / respuestas, sobre todas las respuestas
  · Dominio de un tema    : media de Mastery.nivel entre los estudiantes que lo tocaron
  · Tema completado       : tiene al menos una cápsula completada por ese estudiante

EMBUDO LEAN:
  · Tasa de inicio        : estudiantes con >=1 StudySession / registrados
  · Tasa de finalización  : de los que iniciaron, cuántos completaron >=1 cápsula
  · Retorno D1            : por cohorte diaria — de los activos el día X, cuántos
                            registran actividad el día X+1. El día en curso sale
                            marcado como parcial: su "día siguiente" aún no existe.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import Date, Integer, distinct, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Capsule, Mastery, Response, Student, StudySession, Topic,
)

VENTANA_ACTIVIDAD_DIAS = 7


async def resumen(s: AsyncSession) -> dict:
    corte = datetime.now(timezone.utc) - timedelta(days=VENTANA_ACTIVIDAD_DIAS)
    correcta = func.cast(Response.es_correcta, Integer)

    total_estudiantes = await s.scalar(
        select(func.count(Student.id)).where(Student.consentimiento.is_(True))
    ) or 0

    estudiantes_activos = await s.scalar(
        select(func.count(distinct(Response.student_id)))
        .where(Response.respondido_en >= corte)
    ) or 0

    capsulas_entregadas = await s.scalar(
        select(func.count(StudySession.id))
        .where(StudySession.completada.is_(True))
    ) or 0

    total_temas = await s.scalar(
        select(func.count(Topic.id)).where(Topic.activo.is_(True))
    ) or 0

    n_resp, n_ok = (await s.execute(
        select(func.count(Response.id), func.coalesce(func.sum(correcta), 0))
    )).one()

    # --- Dominio por tema (incluye temas sin datos, con dominio 0) ---
    filas_temas = (await s.execute(
        select(
            Topic.id, Topic.nombre,
            func.coalesce(func.avg(Mastery.nivel), 0.0),
            func.coalesce(func.sum(Mastery.numero_evidencias), 0),
        )
        .join(Mastery, Mastery.topic_id == Topic.id, isouter=True)
        .where(Topic.activo.is_(True))
        .group_by(Topic.id, Topic.nombre, Topic.orden)
        .order_by(Topic.orden)
    )).all()

    # --- Progreso individual ---
    respuestas_por_est = (
        select(
            Response.student_id.label("sid"),
            func.count(Response.id).label("n"),
            func.coalesce(func.sum(correcta), 0).label("ok"),
            func.max(Response.respondido_en).label("ultima"),
        )
        .group_by(Response.student_id)
        .subquery()
    )

    temas_por_est = (
        select(
            StudySession.student_id.label("sid"),
            func.count(distinct(Capsule.topic_id)).label("temas"),
        )
        .join(Capsule, Capsule.id == StudySession.capsule_id)
        .where(StudySession.completada.is_(True))
        .group_by(StudySession.student_id)
        .subquery()
    )

    filas_est = (await s.execute(
        select(
            Student.codigo_anonimo,
            func.coalesce(temas_por_est.c.temas, 0),
            func.coalesce(respuestas_por_est.c.ok, 0),
            func.coalesce(respuestas_por_est.c.n, 0),
            respuestas_por_est.c.ultima,
        )
        .join(respuestas_por_est, respuestas_por_est.c.sid == Student.id, isouter=True)
        .join(temas_por_est, temas_por_est.c.sid == Student.id, isouter=True)
        .where(Student.consentimiento.is_(True))
        .order_by(respuestas_por_est.c.ultima.desc().nullslast())
    )).all()

    # --- Embudo Lean: inicio -> finalización -> retorno D1 ---
    iniciaron = await s.scalar(
        select(func.count(distinct(StudySession.student_id)))
    ) or 0

    completaron = await s.scalar(
        select(func.count(distinct(StudySession.student_id)))
        .where(StudySession.completada.is_(True))
    ) or 0

    # Pares (estudiante, día con actividad). El LEFT JOIN contra sí misma
    # busca al mismo estudiante en día+1: si aparece, volvió.
    # El cast a Date es necesario: date + interval devuelve timestamp en
    # PostgreSQL, y sin él la comparación nunca coincide.
    dias = (
        select(
            StudySession.student_id.label("sid"),
            func.date(StudySession.iniciada_en).label("dia"),
        )
        .distinct()
        .subquery()
    )
    d2 = dias.alias("d2")

    filas_retorno = (await s.execute(
        select(
            dias.c.dia,
            func.count().label("activos"),
            func.count(d2.c.sid).label("volvieron"),
        )
        .join(
            d2,
            (d2.c.sid == dias.c.sid)
            & (d2.c.dia == func.cast(dias.c.dia + text("INTERVAL '1 day'"), Date)),
            isouter=True,
        )
        .group_by(dias.c.dia)
        .order_by(dias.c.dia)
    )).all()

    hoy = datetime.now(timezone.utc).date()

    return {
        "estudiantes_activos": estudiantes_activos,
        "total_estudiantes": total_estudiantes,
        "capsulas_entregadas": capsulas_entregadas,
        "tasa_acierto": (n_ok / n_resp) if n_resp else 0.0,
        "dominio_por_tema": [
            {"topic_id": tid, "nombre": nombre,
             "dominio": float(dom), "respuestas": int(ev)}
            for tid, nombre, dom, ev in filas_temas
        ],
        "estudiantes": [
            {"codigo_anonimo": cod, "temas_completados": int(temas),
             "total_temas": total_temas, "aciertos": int(ok),
             "respuestas": int(n), "ultima_actividad": ultima}
            for cod, temas, ok, n, ultima in filas_est
        ],
        "embudo": {
            "registrados": total_estudiantes,
            "iniciaron": iniciaron,
            "completaron": completaron,
            "retorno": [
                {"dia": d, "activos": int(a), "volvieron": int(v),
                 "parcial": d >= hoy}
                for d, a, v in filas_retorno
            ],
        },
    }