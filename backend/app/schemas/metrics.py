"""DTOs del dashboard docente."""

from datetime import date, datetime

from pydantic import BaseModel


class CeldaMapa(BaseModel):
    """Una casilla del mapa del curso: un estudiante en un tema."""
    topic_id: str
    dominio: float | None = None   # None = sin evidencia; distinto de 0.0
    respuestas: int = 0
    completadas: int = 0           # cápsulas del tema ya terminadas


class DominioTema(BaseModel):
    topic_id: str
    nombre: str
    unidad: int | None = None
    dominio: float
    respuestas: int
    capsulas: int = 0              # cápsulas activas del tema


class ProgresoEstudiante(BaseModel):
    codigo_anonimo: str
    temas_completados: int
    total_temas: int
    aciertos: int
    respuestas: int
    ultima_actividad: datetime | None = None
    tema_actual: str | None = None     # último tema con actividad
    unidad_actual: int | None = None
    celdas: list[CeldaMapa] = []


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


# ------------------------------------------------- detalle individual

class DetalleTema(BaseModel):
    topic_id: str
    nombre: str
    unidad: int | None = None
    dominio: float | None = None   # None = sin evidencia
    respuestas: int = 0
    aciertos: int = 0
    capsulas_total: int = 0
    capsulas_completadas: int = 0
    ultimo_repaso: datetime | None = None
    proximo_repaso: datetime | None = None


class DetalleEstudiante(BaseModel):
    """Ficha completa de un estudiante. Se pide al desplegar su fila.

    No va dentro del resumen a propósito: cargar esto para sesenta
    estudiantes en cada visita al panel haría lento lo que hoy es inmediato.
    """
    codigo_anonimo: str
    registrado_en: datetime
    ultima_actividad: datetime | None = None
    tiempo_estudio_seg: float = 0.0
    sesiones_iniciadas: int = 0       # solo cerradas: ver metrics.py
    sesiones_completadas: int = 0
    sesiones_abandonadas: int = 0
    repasos_vencidos: int = 0
    proximo_repaso: datetime | None = None
    temas: list[DetalleTema] = []