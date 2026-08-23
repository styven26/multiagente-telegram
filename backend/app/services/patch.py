"""Centinela para PATCH parciales.

Un campo que admite nulos tiene tres estados posibles en una petición:
  - no vino          -> no tocar
  - vino con texto   -> asignar
  - vino como null   -> vaciar

Con `None` solo se distinguen dos. Este objeto marca el primero.
"""

from typing import Any

SIN_CAMBIO: Any = object()


def limpiar(valor: Any) -> str | None:
    """Normaliza texto opcional: '' y '   ' se guardan como NULL."""
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto or None