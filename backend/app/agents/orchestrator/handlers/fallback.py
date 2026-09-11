"""Respuesta de reserva para texto que ningún otro manejador reconoce. [Ciclo 1]

Se registra el último: aiogram recorre los routers en orden, así que aquí solo
llega lo que nadie atendió. Sin esto, el estudiante que escribe «hola» no recibe
nada y no puede distinguir un bot que no le entiende de uno caído.

El aviso se borra solo, igual que el bloqueo durante el quiz: si se quedara en
el chat, cada mensaje suelto empujaría hacia arriba la sección activa y el
estudiante perdería de vista los botones con los que sí puede seguir.
"""

import asyncio
import contextlib

from aiogram import F, Router
from aiogram.types import Message

from app.agents.base import estudiante_por_telegram as _estudiante
from app.db.base import SessionLocal

router = Router(name="fallback")

SEGUNDOS_VISIBLE = 2


@router.message(F.text)
async def texto_no_reconocido(message: Message):
    async with SessionLocal() as s:
        est = await _estudiante(s, message.from_user.id)

    if est is None:
        await message.answer("Para empezar, escribe /start.")
        return

    aviso = await message.answer(
        "No entiendo los mensajes escritos. Usa los botones del menú 👇"
    )

    await asyncio.sleep(SEGUNDOS_VISIBLE)
    for m in (message, aviso):
        with contextlib.suppress(Exception):
            await m.delete()