"""Respuesta de reserva para texto que ningún otro manejador reconoce. [Ciclo 1]

Se registra el último: aiogram recorre los routers en orden, así que aquí solo
llega lo que nadie atendió. Sin esto, el estudiante que escribe «hola» no recibe
nada y no puede distinguir un bot que no le entiende de uno caído.

El aviso lleva el menú fijo: el estudiante puede escribir justo cuando el menú
está oculto (salió de una cápsula cerrando Telegram), y un aviso que remite a
«los botones de abajo» sin botones lo deja sin salida. Se conserva un solo
aviso a la vez: el nuevo se envía antes de borrar el anterior, porque Telegram
retira el teclado fijo junto con el mensaje que lo trajo.
"""

import contextlib

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.agents.base import estudiante_por_telegram as _estudiante, teclado_principal
from app.db.base import SessionLocal

router = Router(name="fallback")


@router.message(F.text)
async def texto_no_reconocido(message: Message, state: FSMContext):
    async with SessionLocal() as s:
        est = await _estudiante(s, message.from_user.id)
        teclado = await teclado_principal(s, est.id) if est else None

    if est is None:
        await message.answer("Para empezar, escribe /start.")
        return

    with contextlib.suppress(Exception):
        await message.delete()

    anterior = (await state.get_data()).get("fallback_msg_id")

    aviso = await message.answer(
        "No entiendo los mensajes escritos. Usa los botones del menú 👇",
        reply_markup=teclado,
    )
    await state.update_data(fallback_msg_id=aviso.message_id)

    if anterior:
        with contextlib.suppress(Exception):
            await message.bot.delete_message(message.chat.id, anterior)