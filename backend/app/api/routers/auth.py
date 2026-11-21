"""Inicio de sesion de docentes."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import docente_actual
from app.core import limites
from app.core.security import crear_token, verificar_password
from app.db.base import get_session
from app.db.models import Teacher
from app.schemas.teacher import LoginIn, TeacherOut, TokenOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
async def login(datos: LoginIn, request: Request,
                s: AsyncSession = Depends(get_session)):
    # Antes de consultar nada: si ya hubo demasiados fallos, ni se mira.
    limites.comprobar(request, datos.email)

    docente = await s.scalar(
        select(Teacher).where(func.lower(Teacher.email) == datos.email.lower())
    )

    if docente is None or not verificar_password(datos.password, docente.password_hash):
        limites.anotar_fallo(request, datos.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contrasena incorrectos",
        )
    if not docente.activo:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")

    limites.limpiar(request, datos.email)

    return TokenOut(
        access_token=crear_token(docente.id, docente.rol),
        docente=TeacherOut.model_validate(docente),
    )


@router.get("/me", response_model=TeacherOut)
async def yo(docente: Teacher = Depends(docente_actual)):
    return docente