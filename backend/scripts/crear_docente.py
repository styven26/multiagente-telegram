"""Crea o actualiza un docente con contrasena."""

import asyncio
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select

from app.core.security import hash_password
from app.db.base import SessionLocal, engine
from app.db.models import Teacher


async def main():
    nombre = input("Nombre: ").strip()
    email = input("Email: ").strip().lower()
    rol = input("Rol [docente/investigador/administrador]: ").strip() or "docente"
    if rol not in {"docente", "investigador", "administrador"}:
        print("Rol invalido.")
        return

    p1 = getpass.getpass("Contrasena (min. 8): ")
    if len(p1) < 8:
        print("Muy corta.")
        return
    if p1 != getpass.getpass("Repetir: "):
        print("No coinciden.")
        return

    async with SessionLocal() as s:
        existente = await s.scalar(
            select(Teacher).where(func.lower(Teacher.email) == email)
        )
        if existente:
            existente.password_hash = hash_password(p1)
            existente.nombre = nombre
            existente.rol = rol
            existente.activo = True
            accion = "actualizado"
        else:
            s.add(Teacher(nombre=nombre, email=email, rol=rol,
                          password_hash=hash_password(p1), activo=True))
            accion = "creado"
        await s.commit()

    await engine.dispose()
    print(f"Docente {accion}: {email}")


asyncio.run(main())