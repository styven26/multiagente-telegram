"""Banco de preguntas. Las respuestas de los estudiantes (tabla responses)
apuntan a question_id, así que las preguntas se desactivan, nunca se borran.

INVARIANTE CRÍTICA: `correcta` es el índice dentro de `opciones`. Toda ruta que
modifique una de las dos debe revalidar la otra, o las respuestas se califican mal.
"""
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Capsule, Event, Question
from app.services.patch import SIN_CAMBIO, limpiar

async def _capsula_o_error(session: AsyncSession, capsule_id: str) -> Capsule:
    capsula = await session.get(Capsule, capsule_id)
    if capsula is None:
        raise LookupError(capsule_id)
    return capsula


async def listar(session: AsyncSession, capsule_id: str,
                 solo_activas: bool = False) -> list[Question]:
    await _capsula_o_error(session, capsule_id)
    q = select(Question).where(Question.capsule_id == capsule_id).order_by(Question.id)
    if solo_activas:
        q = q.where(Question.activo.is_(True))
    return list(await session.scalars(q))


async def crear(session: AsyncSession, capsule_id: str, tipo: str, enunciado: str,
                opciones: list[str], correcta: int, retroalimentacion: str | None,
                dificultad: int, actor_id: int | None) -> Question:
    capsula = await _capsula_o_error(session, capsule_id)

    if correcta >= len(opciones):
        raise ValueError("El índice de la respuesta correcta no existe")

    pregunta = Question(
        capsule_id=capsule_id,
        topic_id=capsula.topic_id,      # se hereda: nunca se elige aparte
        tipo=tipo,
        enunciado=enunciado,
        opciones=opciones,
        correcta=correcta,
        retroalimentacion=retroalimentacion,
        dificultad=dificultad,
        activo=True,
    )
    session.add(pregunta)
    session.add(Event(ciclo=1, tipo="admin_pregunta_creada",
                      payload={"capsule_id": capsule_id, "actor": actor_id}))
    await session.commit()
    await session.refresh(pregunta)
    return pregunta


async def actualizar(session: AsyncSession, question_id: int, actor_id: int | None,
                     tipo: str | None = None,
                     enunciado: str | None = None, opciones: list[str] | None = None,
                     correcta: int | None = None,
                     retroalimentacion: Any = SIN_CAMBIO,
                     dificultad: int | None = None) -> Question:
    pregunta = await session.get(Question, question_id)
    if pregunta is None:
        raise LookupError(str(question_id))

    # Se valida el par completo, con los valores que quedarán tras el cambio.
    ops = opciones if opciones is not None else list(pregunta.opciones)
    cor = correcta if correcta is not None else pregunta.correcta
    if cor >= len(ops):
        raise ValueError(
            f"La respuesta correcta apunta a la opción {cor}, pero quedarían "
            f"{len(ops)} opciones. Marca cuál es la correcta antes de guardar."
        )

    tp = tipo if tipo is not None else pregunta.tipo
    if tp == "verdadero_falso" and len(ops) != 2:
        raise ValueError("Verdadero/Falso debe tener exactamente 2 opciones")

    cambios = {}
    if tipo is not None and tipo != pregunta.tipo:
        cambios["tipo"] = [pregunta.tipo, tipo]
        pregunta.tipo = tipo
    if enunciado is not None and enunciado != pregunta.enunciado:
        cambios["enunciado"] = ["...", "..."]
        pregunta.enunciado = enunciado
    if opciones is not None:
        cambios["opciones"] = [list(pregunta.opciones), ops]
        pregunta.opciones = ops
    if correcta is not None and correcta != pregunta.correcta:
        cambios["correcta"] = [pregunta.correcta, correcta]
        pregunta.correcta = correcta
    if retroalimentacion is not SIN_CAMBIO:
        nueva = limpiar(retroalimentacion)
        if nueva != pregunta.retroalimentacion:
            cambios["retroalimentacion"] = [bool(pregunta.retroalimentacion), bool(nueva)]
            pregunta.retroalimentacion = nueva
    if dificultad is not None and dificultad != pregunta.dificultad:
        cambios["dificultad"] = [pregunta.dificultad, dificultad]
        pregunta.dificultad = dificultad

    if cambios:
        session.add(Event(ciclo=1, tipo="admin_pregunta_editada",
                          payload={"question_id": question_id, "cambios": cambios,
                                   "actor": actor_id}))
    await session.commit()
    await session.refresh(pregunta)
    return pregunta


async def alternar_visibilidad(session: AsyncSession, question_id: int,
                               actor_id: int | None) -> Question:
    pregunta = await session.get(Question, question_id)
    if pregunta is None:
        raise LookupError(str(question_id))
    pregunta.activo = not pregunta.activo
    session.add(Event(ciclo=1, tipo="admin_pregunta_visibilidad",
                      payload={"question_id": question_id, "activo": pregunta.activo,
                               "actor": actor_id}))
    await session.commit()
    await session.refresh(pregunta)
    return pregunta