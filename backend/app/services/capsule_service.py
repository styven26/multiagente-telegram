"""Lógica de micro-cápsulas. Igual que los temas: el `id` es inmutable
(aparece en study_sessions y spaced_repetition). Se desactivan, no se borran.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Capsule, Event, Topic

async def _tema_o_error(session: AsyncSession, topic_id: str) -> Topic:
    tema = await session.get(Topic, topic_id)
    if tema is None:
        raise LookupError(topic_id)
    return tema


async def listar(session: AsyncSession, topic_id: str,
                 solo_activos: bool = False) -> list[Capsule]:
    await _tema_o_error(session, topic_id)
    q = select(Capsule).where(Capsule.topic_id == topic_id).order_by(Capsule.orden)
    if solo_activos:
        q = q.where(Capsule.activo.is_(True))
    return list(await session.scalars(q))


async def crear(session: AsyncSession, topic_id: str, titulo: str, objetivo: str,
                contenido: str, duracion_min: int, dificultad: int,
                actor_id: int | None) -> Capsule:
    await _tema_o_error(session, topic_id)

    siguiente = (await session.scalar(
        select(func.max(Capsule.orden)).where(Capsule.topic_id == topic_id)
    ) or 0) + 1

    base = topic_id[:50]
    cid = f"{base}_C{siguiente}"
    sufijo = 1
    while await session.get(Capsule, cid):
        sufijo += 1
        cid = f"{base}_C{siguiente}_{sufijo}"

    capsula = Capsule(
        id=cid, topic_id=topic_id, titulo=titulo, objetivo=objetivo,
        contenido=contenido, orden=siguiente, duracion_min=duracion_min,
        dificultad=dificultad, activo=True,
    )
    session.add(capsula)
    session.add(Event(ciclo=1, tipo="admin_capsula_creada",
                      payload={"capsule_id": cid, "topic_id": topic_id,
                               "actor": actor_id}))
    await session.commit()
    await session.refresh(capsula)
    return capsula


async def actualizar(session: AsyncSession, capsule_id: str, actor_id: int | None,
                     titulo: str | None = None, objetivo: str | None = None,
                     contenido: str | None = None, duracion_min: int | None = None,
                     dificultad: int | None = None) -> Capsule:
    capsula = await session.get(Capsule, capsule_id)
    if capsula is None:
        raise LookupError(capsule_id)

    cambios = {}
    if titulo is not None and titulo != capsula.titulo:
        cambios["titulo"] = [capsula.titulo, titulo]
        capsula.titulo = titulo
    if objetivo is not None and objetivo != capsula.objetivo:
        cambios["objetivo"] = ["...", "..."]
        capsula.objetivo = objetivo
    if contenido is not None and contenido != capsula.contenido:
        cambios["contenido"] = ["...", "..."]
        capsula.contenido = contenido
    if duracion_min is not None and duracion_min != capsula.duracion_min:
        cambios["duracion_min"] = [capsula.duracion_min, duracion_min]
        capsula.duracion_min = duracion_min
    if dificultad is not None and dificultad != capsula.dificultad:
        cambios["dificultad"] = [capsula.dificultad, dificultad]
        capsula.dificultad = dificultad

    if cambios:
        session.add(Event(ciclo=1, tipo="admin_capsula_editada",
                          payload={"capsule_id": capsule_id, "cambios": cambios,
                                   "actor": actor_id}))
    await session.commit()
    await session.refresh(capsula)
    return capsula


async def alternar_visibilidad(session: AsyncSession, capsule_id: str,
                               actor_id: int | None) -> Capsule:
    capsula = await session.get(Capsule, capsule_id)
    if capsula is None:
        raise LookupError(capsule_id)
    capsula.activo = not capsula.activo
    session.add(Event(ciclo=1, tipo="admin_capsula_visibilidad",
                      payload={"capsule_id": capsule_id, "activo": capsula.activo,
                               "actor": actor_id}))
    await session.commit()
    await session.refresh(capsula)
    return capsula