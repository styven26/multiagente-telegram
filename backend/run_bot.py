"""Punto de entrada del bot."""

import asyncio

from app.agents.orchestrator.bot import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nBot detenido.")