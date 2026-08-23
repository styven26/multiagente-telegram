"""Arranque del Agente Orquestador (aiogram 3). [Ciclo 1]"""

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.agents.orchestrator.handlers import menu, salir, start
from app.agents.orchestrator.middlewares import ConsentimientoMiddleware
from app.config import settings
from app.agents.spaced_repetition.scheduler import crear_scheduler

logger = logging.getLogger(__name__)

COMANDOS = [
    BotCommand(command="start", description="Iniciar / registrarse"),
    BotCommand(command="menu", description="Menú principal"),
    BotCommand(command="salir", description="Retirarme del estudio"),
]


def crear_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.outer_middleware(ConsentimientoMiddleware())
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(salir.router)
    return dp
    

async def main() -> None:
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = crear_dispatcher()

    me = await bot.get_me()
    logger.info("Bot conectado como @%s (id=%s)", me.username, me.id)

    await bot.set_my_commands(COMANDOS)
    await bot.delete_webhook(drop_pending_updates=True)

    scheduler = crear_scheduler(bot)
    scheduler.start()
    logger.info("Planificador de repasos activo (cada %s min)", 5)

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()