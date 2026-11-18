"""Métricas del dashboard. [Ciclo 1 - Lean]

DEFINICIONES (fíjalas aquí y cítalas igual en la tesis):
  · Estudiante registrado : consentimiento = TRUE
  · Estudiante activo     : respondió al menos una pregunta en los últimos 7 días
  · Cápsula entregada     : StudySession con completada = TRUE
  · Tasa de acierto       : aciertos / respuestas, sobre todas las respuestas
  · Dominio de un tema    : media de Mastery.nivel entre los estudiantes que lo tocaron
  · Tema completado       : tiene al menos una cápsula completada por ese estudiante

EMBUDO LEAN:
  · Tasa de inicio        : estudiantes con >=1 StudySession cerrada / registrados.
                            Igual que abajo, solo cuentan sesiones cerradas: una
                            en curso todavía no dice nada del estudiante.
  · Tasa de finalización  : de los que iniciaron, cuántos completaron >=1 cápsula.
                            Solo cuenta sesiones cerradas (finalizada_en no nulo):
                            una sesión en curso aún no es un abandono.
  · Retorno D1            : por cohorte diaria — de los activos el día X, cuántos
                            registran actividad el día X+1. El día en curso sale
                            marcado como parcial: su "día siguiente" aún no existe.

MAPA DEL CURSO:
  Una casilla por (estudiante, tema). `dominio` es None cuando no hay evidencia,
  que no es lo mismo que 0.0: un cero se lee como "lo hizo mal" y lo que pasa es
  que no lo ha hecho.
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import Date, Integer, distinct, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import (
    Capsule, Mastery, Response, SpacedRepetition, Student, StudySession, Topic,
)

VENTANA_ACTIVIDAD_DIAS = 7


def _cohorte():
    """Condición de cohorte para el dashboard.

    Sin COHORTE_ACTUAL definida no filtra nada, así el entorno de desarrollo
    sigue viendo todo. Con ella, las pruebas del desarrollador quedan fuera de
    las métricas del estudio sin necesidad de borrar el histórico.
    """
    if settings.COHORTE_ACTUAL is None:
        return True
    return Student.cohorte == settings.COHORTE_ACTUAL


async def resumen(s: AsyncSession) -> dict:
    corte = datetime.now(timezone.utc) - timedelta(days=VENTANA_ACTIVIDAD_DIAS)
    correcta = func.cast(Response.es_correcta, Integer)

    total_estudiantes = await s.scalar(
        select(func.count(Student.id))
        .where(Student.consentimiento.is_(True), _cohorte())
    ) or 0

    estudiantes_activos = await s.scalar(
        select(func.count(distinct(Response.student_id)))
        .join(Student, Student.id == Response.student_id)
        .where(Response.respondido_en >= corte, _cohorte())
    ) or 0

    capsulas_entregadas = await s.scalar(
        select(func.count(StudySession.id))
        .join(Student, Student.id == StudySession.student_id)
        .where(StudySession.completada.is_(True), _cohorte())
    ) or 0

    total_temas = await s.scalar(
        select(func.count(Topic.id)).where(Topic.activo.is_(True))
    ) or 0

    n_resp, n_ok = (await s.execute(
        select(func.count(Response.id), func.coalesce(func.sum(correcta), 0))
        .join(Student, Student.id == Response.student_id)
        .where(_cohorte())
    )).one()

    # --- Dominio por tema (incluye temas sin datos, con dominio 0) ---
    # El filtro de cohorte va dentro de la subconsulta, no en el WHERE final:
    # tras un LEFT JOIN, un tema sin datos de la cohorte tiene cohorte NULL, y
    # el WHERE lo eliminaría en vez de mostrarlo con dominio 0.
    mastery_cohorte = (
        select(Mastery.topic_id, Mastery.nivel, Mastery.numero_evidencias)
        .join(Student, Student.id == Mastery.student_id)
        .where(_cohorte())
        .subquery()
    )

    filas_temas = (await s.execute(
        select(
            Topic.id, Topic.nombre, Topic.unidad,
            func.coalesce(func.avg(mastery_cohorte.c.nivel), 0.0),
            func.coalesce(func.sum(mastery_cohorte.c.numero_evidencias), 0),
        )
        .join(mastery_cohorte, mastery_cohorte.c.topic_id == Topic.id,
              isouter=True)
        .where(Topic.activo.is_(True))
        .group_by(Topic.id, Topic.nombre, Topic.unidad, Topic.orden)
        .order_by(Topic.orden)
    )).all()

    # Cápsulas activas por tema: el denominador de "0 de 1" en el detalle.
    capsulas_por_tema = dict((await s.execute(
        select(Capsule.topic_id, func.count(Capsule.id))
        .where(Capsule.activo.is_(True))
        .group_by(Capsule.topic_id)
    )).all())

    # --- Progreso individual ---
    respuestas_por_est = (
        select(
            Response.student_id.label("sid"),
            func.count(Response.id).label("n"),
            func.coalesce(func.sum(correcta), 0).label("ok"),
            func.max(Response.respondido_en).label("ultima"),
        )
        .join(Student, Student.id == Response.student_id)
        .where(_cohorte())
        .group_by(Response.student_id)
        .subquery()
    )

    temas_por_est = (
        select(
            StudySession.student_id.label("sid"),
            func.count(distinct(Capsule.topic_id)).label("temas"),
        )
        .join(Capsule, Capsule.id == StudySession.capsule_id)
        .join(Student, Student.id == StudySession.student_id)
        .where(StudySession.completada.is_(True), _cohorte())
        .group_by(StudySession.student_id)
        .subquery()
    )

    filas_est = (await s.execute(
        select(
            Student.id,
            Student.codigo_anonimo,
            func.coalesce(temas_por_est.c.temas, 0),
            func.coalesce(respuestas_por_est.c.ok, 0),
            func.coalesce(respuestas_por_est.c.n, 0),
            respuestas_por_est.c.ultima,
        )
        .join(respuestas_por_est, respuestas_por_est.c.sid == Student.id, isouter=True)
        .join(temas_por_est, temas_por_est.c.sid == Student.id, isouter=True)
        .where(Student.consentimiento.is_(True), _cohorte())
        .order_by(respuestas_por_est.c.ultima.desc().nullslast())
    )).all()

    # --- Mapa del curso: una casilla por (estudiante, tema) ---
    # Tres consultas agrupadas en vez de una por estudiante: con sesenta
    # estudiantes y siete temas, lo segundo serían 420 viajes a la base.
    resp_celda = {(sid, tid): (int(n), int(ok)) for sid, tid, n, ok in (await s.execute(
        select(Response.student_id, Response.topic_id,
               func.count(Response.id), func.coalesce(func.sum(correcta), 0))
        .join(Student, Student.id == Response.student_id)
        .where(_cohorte())
        .group_by(Response.student_id, Response.topic_id)
    )).all()}

    dom_celda = {(sid, tid): float(nivel) for sid, tid, nivel in (await s.execute(
        select(Mastery.student_id, Mastery.topic_id, Mastery.nivel)
        .join(Student, Student.id == Mastery.student_id)
        .where(Mastery.numero_evidencias > 0, _cohorte())
    )).all()}

    caps_celda = {(sid, tid): int(n) for sid, tid, n in (await s.execute(
        select(StudySession.student_id, Capsule.topic_id,
               func.count(distinct(Capsule.id)))
        .join(Capsule, Capsule.id == StudySession.capsule_id)
        .join(Student, Student.id == StudySession.student_id)
        .where(StudySession.completada.is_(True), _cohorte())
        .group_by(StudySession.student_id, Capsule.topic_id)
    )).all()}

    # Tema de la última respuesta: la columna "En qué va" de la tabla.
    # DISTINCT ON exige que el ORDER BY empiece por la misma columna.
    tema_actual = {sid: tid for sid, tid in (await s.execute(
        select(Response.student_id, Response.topic_id)
        .join(Student, Student.id == Response.student_id)
        .where(_cohorte())
        .distinct(Response.student_id)
        .order_by(Response.student_id, Response.respondido_en.desc())
    )).all()}

    nombre_tema = {tid: (nombre, unidad) for tid, nombre, unidad, _, _ in filas_temas}

    # --- Embudo Lean: inicio -> finalización -> retorno D1 ---
    # Solo sesiones resueltas: quien lleva cinco minutos leyendo no ha
    # abandonado nada todavía, y contarlo como "inició sin completar" hunde
    # la tasa mientras el estudiante sigue estudiando.
    iniciaron = await s.scalar(
        select(func.count(distinct(StudySession.student_id)))
        .join(Student, Student.id == StudySession.student_id)
        .where(StudySession.finalizada_en.is_not(None), _cohorte())
    ) or 0

    completaron = await s.scalar(
        select(func.count(distinct(StudySession.student_id)))
        .join(Student, Student.id == StudySession.student_id)
        .where(StudySession.completada.is_(True),
               StudySession.finalizada_en.is_not(None), _cohorte())
    ) or 0

    # Pares (estudiante, día con actividad). El LEFT JOIN contra sí misma
    # busca al mismo estudiante en día+1: si aparece, volvió.
    # El cast a Date es necesario: date + interval devuelve timestamp en
    # PostgreSQL, y sin él la comparación nunca coincide.
    dias = (
        select(
            StudySession.student_id.label("sid"),
            # El día se cuenta en hora local: en UTC, lo que se estudia
            # después de las 19:00 en Guayaquil caería en el día siguiente.
            func.date(func.timezone(settings.TIMEZONE, StudySession.iniciada_en)).label("dia"),
        )
        .join(Student, Student.id == StudySession.student_id)
        .where(_cohorte())
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

    hoy = datetime.now(ZoneInfo(settings.TIMEZONE)).date()

    def _celdas(sid: int) -> list[dict]:
        salida = []
        for tid, _nombre, _unidad, _dom, _ev in filas_temas:
            n, _ok = resp_celda.get((sid, tid), (0, 0))
            salida.append({
                "topic_id": tid,
                "dominio": dom_celda.get((sid, tid)),
                "respuestas": n,
                "completadas": caps_celda.get((sid, tid), 0),
            })
        return salida

    estudiantes = []
    for sid, cod, temas, ok, n, ultima in filas_est:
        tid = tema_actual.get(sid)
        nombre, unidad = nombre_tema.get(tid, (None, None)) if tid else (None, None)
        estudiantes.append({
            "codigo_anonimo": cod,
            "temas_completados": int(temas),
            "total_temas": total_temas,
            "aciertos": int(ok),
            "respuestas": int(n),
            "ultima_actividad": ultima,
            "tema_actual": nombre,
            "unidad_actual": unidad,
            "celdas": _celdas(sid),
        })

    return {
        "estudiantes_activos": estudiantes_activos,
        "total_estudiantes": total_estudiantes,
        "capsulas_entregadas": capsulas_entregadas,
        "tasa_acierto": (n_ok / n_resp) if n_resp else 0.0,
        "dominio_por_tema": [
            {"topic_id": tid, "nombre": nombre, "unidad": unidad,
             "dominio": float(dom), "respuestas": int(ev),
             "capsulas": int(capsulas_por_tema.get(tid, 0))}
            for tid, nombre, unidad, dom, ev in filas_temas
        ],
        "estudiantes": estudiantes,
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


async def detalle_estudiante(s: AsyncSession, codigo: str) -> dict:
    """Ficha de un estudiante, para la fila desplegada de la tabla.

    Se pide bajo demanda y no dentro de `resumen`: son siete consultas por
    persona, y traerlas para toda la cohorte en cada carga del panel cambiaría
    una respuesta inmediata por varios segundos de espera.
    """
    est = await s.scalar(
        select(Student).where(Student.codigo_anonimo == codigo)
    )
    if est is None:
        raise LookupError(codigo)

    correcta = func.cast(Response.es_correcta, Integer)
    ahora = datetime.now(timezone.utc)

    cerradas, completadas, tiempo = (await s.execute(
        select(
            func.count(StudySession.id),
            func.count(StudySession.id).filter(StudySession.completada.is_(True)),
            func.coalesce(func.sum(StudySession.duracion_seg), 0.0),
        )
        .where(StudySession.student_id == est.id,
               StudySession.finalizada_en.is_not(None))
    )).one()

    ultima = await s.scalar(
        select(func.max(Response.respondido_en))
        .where(Response.student_id == est.id)
    )

    # Solo cápsulas activas: un repaso de contenido que el docente retiró no
    # le aparece al estudiante, así que tampoco debe contarse como vencido.
    vencidos = await s.scalar(
        select(func.count(SpacedRepetition.id))
        .join(Capsule, Capsule.id == SpacedRepetition.capsule_id)
        .where(SpacedRepetition.student_id == est.id,
               SpacedRepetition.activo.is_(True),
               Capsule.activo.is_(True),
               SpacedRepetition.proxima_revision_en.is_not(None),
               SpacedRepetition.proxima_revision_en <= ahora)
    ) or 0

    proximo = await s.scalar(
        select(func.min(SpacedRepetition.proxima_revision_en))
        .join(Capsule, Capsule.id == SpacedRepetition.capsule_id)
        .where(SpacedRepetition.student_id == est.id,
               SpacedRepetition.activo.is_(True),
               Capsule.activo.is_(True),
               SpacedRepetition.proxima_revision_en > ahora)
    )

    resp = {tid: (int(n), int(ok)) for tid, n, ok in (await s.execute(
        select(Response.topic_id, func.count(Response.id),
               func.coalesce(func.sum(correcta), 0))
        .where(Response.student_id == est.id)
        .group_by(Response.topic_id)
    )).all()}

    dom = {tid: float(nivel) for tid, nivel in (await s.execute(
        select(Mastery.topic_id, Mastery.nivel)
        .where(Mastery.student_id == est.id, Mastery.numero_evidencias > 0)
    )).all()}

    caps_total = dict((await s.execute(
        select(Capsule.topic_id, func.count(Capsule.id))
        .where(Capsule.activo.is_(True))
        .group_by(Capsule.topic_id)
    )).all())

    caps_ok = dict((await s.execute(
        select(Capsule.topic_id, func.count(distinct(Capsule.id)))
        .join(StudySession, StudySession.capsule_id == Capsule.id)
        .where(StudySession.student_id == est.id,
               StudySession.completada.is_(True))
        .group_by(Capsule.topic_id)
    )).all())

    repasos = {tid: (ult, prox) for tid, ult, prox in (await s.execute(
        select(SpacedRepetition.topic_id,
               func.max(SpacedRepetition.ultima_revision_en),
               func.min(SpacedRepetition.proxima_revision_en))
        .join(Capsule, Capsule.id == SpacedRepetition.capsule_id)
        .where(SpacedRepetition.student_id == est.id,
               SpacedRepetition.activo.is_(True),
               Capsule.activo.is_(True))
        .group_by(SpacedRepetition.topic_id)
    )).all()}

    temas = (await s.execute(
        select(Topic.id, Topic.nombre, Topic.unidad)
        .where(Topic.activo.is_(True))
        .order_by(Topic.orden)
    )).all()

    return {
        "codigo_anonimo": est.codigo_anonimo,
        "registrado_en": est.creado_en,
        "ultima_actividad": ultima,
        "tiempo_estudio_seg": float(tiempo or 0.0),
        "sesiones_iniciadas": int(cerradas or 0),
        "sesiones_completadas": int(completadas or 0),
        "sesiones_abandonadas": int((cerradas or 0) - (completadas or 0)),
        "repasos_vencidos": int(vencidos),
        "proximo_repaso": proximo,
        "temas": [
            {
                "topic_id": tid,
                "nombre": nombre,
                "unidad": unidad,
                "dominio": dom.get(tid),
                "respuestas": resp.get(tid, (0, 0))[0],
                "aciertos": resp.get(tid, (0, 0))[1],
                "capsulas_total": int(caps_total.get(tid, 0)),
                "capsulas_completadas": int(caps_ok.get(tid, 0)),
                "ultimo_repaso": repasos.get(tid, (None, None))[0],
                "proximo_repaso": repasos.get(tid, (None, None))[1],
            }
            for tid, nombre, unidad in temas
        ],
    }