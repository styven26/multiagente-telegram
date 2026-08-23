"""Lógica de temas. La usan tanto el panel de Telegram como la API del dashboard.

REGLA: el `id` de un tema es inmutable (aparece en responses, mastery y en los
datasets del SAKT). Los temas retirados se desactivan, nunca se borran.
"""
from typing import Any
import re
import unicodedata

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Event, Topic
from app.services.patch import SIN_CAMBIO, limpiar

def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "_", t).strip("_").lower()
    return t[:40] or "tema"

async def _validar_prereq(session: AsyncSession, ids: list[str],
                          topic_id: str | None = None) -> list[str]:
    """Verifica que existan, que no haya autorreferencia y que no formen ciclo."""
    limpios = list(dict.fromkeys(i for i in ids if i))
    if not limpios:
        return []
    if topic_id and topic_id in limpios:
        raise ValueError("Un tema no puede ser prerrequisito de sí mismo")

    existentes = set(await session.scalars(
        select(Topic.id).where(Topic.id.in_(limpios))
    ))
    faltantes = [i for i in limpios if i not in existentes]
    if faltantes:
        raise ValueError("No existen estos temas: " + ", ".join(faltantes))

    if topic_id:
        grafo = {t.id: list(t.prerrequisitos or [])
                 for t in await session.scalars(select(Topic))}
        pila, vistos = list(limpios), set()
        while pila:
            actual = pila.pop()
            if actual == topic_id:
                raise ValueError("Los prerrequisitos formarían un ciclo")
            if actual in vistos:
                continue
            vistos.add(actual)
            pila.extend(grafo.get(actual, []))

    return limpios

async def listar(session: AsyncSession, solo_activos: bool = False) -> list[Topic]:
    q = select(Topic).order_by(Topic.orden)
    if solo_activos:
        q = q.where(Topic.activo.is_(True))
    return list(await session.scalars(q))

async def crear(session: AsyncSession, nombre: str, emoji: str | None,
                descripcion: str | None, actor_id: int | None,
                unidad: int | None = None,
                prerrequisitos: list[str] | None = None) -> Topic:
    siguiente = (await session.scalar(select(func.max(Topic.orden))) or 0) + 1
    tid = f"T{siguiente}_{slug(nombre)}"

    if await session.get(Topic, tid):
        raise ValueError(f"Ya existe un tema con el id {tid}")

    prereq = await _validar_prereq(session, prerrequisitos or [])

    tema = Topic(id=tid, nombre=nombre, descripcion=descripcion, orden=siguiente,
                 unidad=unidad, prerrequisitos=prereq, emoji=emoji, activo=True)
    session.add(tema)
    session.add(Event(ciclo=1, tipo="admin_tema_creado",
                      payload={"topic_id": tid, "unidad": unidad, "actor": actor_id}))
    await session.commit()
    await session.refresh(tema)
    return tema


async def actualizar(session: AsyncSession, topic_id: str, actor_id: int | None,
                     nombre: str | None = None, emoji: Any = SIN_CAMBIO,
                     descripcion: Any = SIN_CAMBIO, unidad: int | None = None,
                     prerrequisitos: list[str] | None = None) -> Topic:
    tema = await session.get(Topic, topic_id)
    if tema is None:
        raise LookupError(topic_id)

    cambios = {}
    if nombre is not None and nombre != tema.nombre:
        cambios["nombre"] = [tema.nombre, nombre]
        tema.nombre = nombre
    if emoji is not SIN_CAMBIO:
        tema.emoji = limpiar(emoji)
    if descripcion is not SIN_CAMBIO:
        tema.descripcion = limpiar(descripcion)
    if unidad is not None and unidad != tema.unidad:
        cambios["unidad"] = [tema.unidad, unidad]
        tema.unidad = unidad
    if prerrequisitos is not None:
        prereq = await _validar_prereq(session, prerrequisitos, topic_id)
        cambios["prerrequisitos"] = [list(tema.prerrequisitos or []), prereq]
        tema.prerrequisitos = prereq

    if cambios:
        session.add(Event(ciclo=1, tipo="admin_tema_editado",
                          payload={"topic_id": topic_id, "cambios": cambios,
                                   "actor": actor_id}))
    await session.commit()
    await session.refresh(tema)
    return tema

async def alternar_visibilidad(session: AsyncSession, topic_id: str,
                               actor_id: int | None) -> Topic:
    tema = await session.get(Topic, topic_id)
    if tema is None:
        raise LookupError(topic_id)
    tema.activo = not tema.activo
    session.add(Event(ciclo=1, tipo="admin_tema_visibilidad",
                      payload={"topic_id": topic_id, "activo": tema.activo,
                               "actor": actor_id}))
    await session.commit()
    await session.refresh(tema)
    return tema