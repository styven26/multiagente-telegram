"""DTOs del dashboard docente."""

from datetime import date, datetime

from pydantic import BaseModel


class DominioTema(BaseModel):
    topic_id: str
    nombre: str
    dominio: float
    respuestas: int


class ProgresoEstudiante(BaseModel):
    codigo_anonimo: str
    temas_completados: int
    total_temas: int
    aciertos: int
    respuestas: int
    ultima_actividad: datetime | None = None

class RetornoDia(BaseModel):
    dia: date
    activos: int
    volvieron: int
    parcial: bool = False        # el día en curso: aún no hay "día siguiente"


class Embudo(BaseModel):
    registrados: int
    iniciaron: int
    completaron: int
    retorno: list[RetornoDia]

class ResumenDocente(BaseModel):
    estudiantes_activos: int
    total_estudiantes: int
    capsulas_entregadas: int
    tasa_acierto: float
    embudo: Embudo
    dominio_por_tema: list[DominioTema]
    estudiantes: list[ProgresoEstudiante]