"""DTOs de autenticacion y docentes."""

from pydantic import BaseModel, EmailStr, Field


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class TeacherOut(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: bool

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    docente: TeacherOut