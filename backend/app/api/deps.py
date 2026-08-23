"""Dependencias compartidas de la API."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decodificar_token
from app.db.base import get_session
from app.db.models import Teacher

esquema = HTTPBearer(auto_error=False)

NO_AUTORIZADO = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciales invalidas o sesion expirada",
    headers={"WWW-Authenticate": "Bearer"},
)


async def docente_actual(
    cred: HTTPAuthorizationCredentials | None = Depends(esquema),
    s: AsyncSession = Depends(get_session),
) -> Teacher:
    if cred is None:
        raise NO_AUTORIZADO
    try:
        payload = decodificar_token(cred.credentials)
        teacher_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise NO_AUTORIZADO

    docente = await s.get(Teacher, teacher_id)
    if docente is None or not docente.activo:
        raise NO_AUTORIZADO
    return docente