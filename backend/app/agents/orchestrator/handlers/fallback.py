"""Respuesta de reserva para texto que ningún otro manejador reconoce. [Ciclo 1]

Se registra el último: aiogram recorre los routers en orden, así que aquí solo
llega lo que nadie atendió. Sin esto, el estudiante que escribe «hola» no recibe
nada y no puede distinguir un bot que no le entiende de uno caído.
"""

from aiogram import F, Router
from aiogram.types import Message

from app.agents.base import estudiante_por_telegram as _estudiante, teclado_principal
from app.db.base import SessionLocal

router = Router(name="fallback")


@router.message(F.text)
async def texto_no_reconocido(message: Message):
    async with SessionLocal() as s:
        est = await _estudiante(s, message.from_user.id)
        if est is None:
            await message.answer("Para empezar, escribe /start.")
            return
        teclado = await teclado_principal(s, est.id)

    await message.answer(
        "No entiendo los mensajes escritos. Usa los botones del menú de abajo 👇",
        reply_markup=teclado,
    )
