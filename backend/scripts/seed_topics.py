"""Carga el grafo de conocimiento (6 temas) en la tabla topics. Idempotente."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.constants import TEMAS
from app.db.base import SessionLocal, engine
from app.db.models import Topic


async def main():
    creados, actualizados = 0, 0
    async with SessionLocal() as s:
        for tid, data in TEMAS.items():
            topic = await s.scalar(select(Topic).where(Topic.id == tid))
            if topic:
                topic.nombre = data["nombre"]
                topic.orden = data["orden"]
                topic.prerrequisitos = data["prerrequisitos"]
                topic.emoji = data["emoji"]
                topic.activo = True
                actualizados += 1
            else:
                s.add(Topic(
                    id=tid,
                    nombre=data["nombre"],
                    descripcion=None,
                    orden=data["orden"],
                    prerrequisitos=data["prerrequisitos"],
                    emoji=data["emoji"],
                    activo=True,
                ))
                creados += 1
        await s.commit()
    await engine.dispose()
    print(f"Temas creados: {creados} | actualizados: {actualizados}")


asyncio.run(main())