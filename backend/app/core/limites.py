"""Freno de fuerza bruta para el inicio de sesion.

En memoria y no en Redis a proposito: la API corre en un solo proceso
(uvicorn sin --workers), asi que un diccionario basta y no suma una
dependencia. Si algun dia se levantan varios workers hay que moverlo a
Redis, que ya esta en la maquina: cada worker llevaria su propio contador
y el limite real se multiplicaria por el numero de workers.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status

VENTANA = timedelta(minutes=15)
MAX_POR_CUENTA = 5     # fallos contra un mismo correo
MAX_POR_IP = 20        # fallos desde una misma IP, contra cualquier correo
TOPE_TABLA = 5000


@dataclass
class _Registro:
    fallos: list[datetime] = field(default_factory=list)


_por_cuenta: dict[str, _Registro] = {}
_por_ip: dict[str, _Registro] = {}


def _vigentes(tabla: dict[str, _Registro], clave: str, ahora: datetime) -> int:
    """Fallos dentro de la ventana. De paso descarta los caducados."""
    reg = tabla.get(clave)
    if reg is None:
        return 0
    reg.fallos = [t for t in reg.fallos if ahora - t < VENTANA]
    if not reg.fallos:
        del tabla[clave]
        return 0
    return len(reg.fallos)


def _purgar(ahora: datetime) -> None:
    """Evita que alguien infle las tablas probando correos inventados."""
    for tabla in (_por_cuenta, _por_ip):
        if len(tabla) > TOPE_TABLA:
            for clave in list(tabla):
                _vigentes(tabla, clave, ahora)


def ip_cliente(request: Request) -> str:
    """La IP real del visitante.

    Detras de Nginx, request.client.host es siempre 127.0.0.1: sin esto los
    dos docentes compartirian contador y se bloquearian entre si. Nginx ya
    envia X-Real-IP, y nadie mas alcanza el puerto 8000.
    """
    return request.headers.get("x-real-ip") or (
        request.client.host if request.client else "desconocida")


def comprobar(request: Request, email: str) -> None:
    """Corta antes de tocar la base de datos si ya hubo demasiados fallos."""
    ahora = datetime.now(timezone.utc)

    if (_vigentes(_por_cuenta, email.lower().strip(), ahora) >= MAX_POR_CUENTA
            or _vigentes(_por_ip, ip_cliente(request), ahora) >= MAX_POR_IP):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Vuelve a intentarlo en 15 minutos.",
            headers={"Retry-After": str(int(VENTANA.total_seconds()))},
        )


def anotar_fallo(request: Request, email: str) -> None:
    ahora = datetime.now(timezone.utc)
    _purgar(ahora)
    for tabla, clave in ((_por_cuenta, email.lower().strip()),
                         (_por_ip, ip_cliente(request))):
        tabla.setdefault(clave, _Registro()).fallos.append(ahora)


def limpiar(request: Request, email: str) -> None:
    """Entrada correcta: se olvida el historial de esa cuenta y esa IP."""
    _por_cuenta.pop(email.lower().strip(), None)
    _por_ip.pop(ip_cliente(request), None)