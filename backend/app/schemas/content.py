"""DTOs de entrada y salida de la API.

Los topes deben coincidir con frontend/src/lib/limites.ts.
Origen de cada límite:
  - String(n) del modelo ORM (Postgres rechaza más).
  - Telegram: 4096 caracteres por mensaje; el bot envía titulo + objetivo +
    contenido juntos, por eso el contenido se topa en 3500.
  - 55 por opción: quiz.py corta el texto del botón a 60 ("A. " + opción).
"""
import re
from pydantic import BaseModel, Field, field_validator, model_validator

# --- Topes compartidos con el frontend ---
MAX_OPCION = 55
TIPOS_VALIDOS = {"opcion_multiple", "verdadero_falso", "respuesta_corta"}

TAGS_OK = {"b", "strong", "i", "em", "u", "s", "code", "pre", "a", "br"}
_ETIQUETA = re.compile(r"</?([a-zA-Z]+)[^>]*>")
_SUELTO = re.compile(r"<|&(?!(amp|lt|gt);)")


def _validar_html(texto: str) -> str:
    """Espejo de validarHTML() en limites.ts. Un `<` suelto → Telegram 400."""
    pila: list[str] = []
    for m in _ETIQUETA.finditer(texto):
        tag = m.group(1).lower()
        if tag not in TAGS_OK:
            raise ValueError(f"Telegram no admite la etiqueta <{tag}>")
        if tag == "br":
            continue
        if m.group(0).startswith("</"):
            if not pila or pila.pop() != tag:
                raise ValueError(f"La etiqueta </{tag}> no cierra correctamente")
        else:
            pila.append(tag)
    if pila:
        raise ValueError(f"Falta cerrar <{pila[-1]}>")
    if _SUELTO.search(_ETIQUETA.sub("", texto)):
        raise ValueError("Escribe &lt; &gt; &amp; en vez de < > & sueltos")
    return texto


def _validar_opciones(v: list[str]) -> list[str]:
    """Limpia, comprueba vacías, repetidas y largo del botón de Telegram."""
    limpias = [o.strip() for o in v]
    if any(not o for o in limpias):
        raise ValueError("Ninguna opción puede estar vacía")
    if len({o.lower() for o in limpias}) != len(limpias):
        raise ValueError("Hay opciones repetidas")
    largas = [o for o in limpias if len(o) > MAX_OPCION]
    if largas:
        raise ValueError(
            f"Cada opción admite {MAX_OPCION} caracteres: el botón de Telegram se corta"
        )
    return limpias


# ============================================================
# TOPICS
# ============================================================

class TopicOut(BaseModel):
    id: str
    nombre: str
    descripcion: str | None = None
    orden: int
    unidad: int | None = None
    emoji: str | None = None
    activo: bool
    prerrequisitos: list[str] = []

    model_config = {"from_attributes": True}

    @field_validator("prerrequisitos", mode="before")
    @classmethod
    def _nulo_a_lista(cls, v):
        return v or []


class TopicCreate(BaseModel):
    nombre: str = Field(min_length=3, max_length=128)
    emoji: str | None = Field(default=None, max_length=8)
    descripcion: str | None = Field(default=None, max_length=300)
    unidad: int | None = Field(default=None, ge=1, le=4)
    prerrequisitos: list[str] = []


class TopicUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=128)
    emoji: str | None = Field(default=None, max_length=8)
    descripcion: str | None = Field(default=None, max_length=300)
    unidad: int | None = Field(default=None, ge=1, le=4)
    prerrequisitos: list[str] | None = None


# ============================================================
# CAPSULES
# ============================================================

class CapsuleOut(BaseModel):
    id: str
    topic_id: str
    titulo: str
    objetivo: str
    contenido: str
    orden: int
    duracion_min: int
    dificultad: int
    activo: bool

    model_config = {"from_attributes": True}


class CapsuleCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=200)
    objetivo: str = Field(min_length=5, max_length=300)
    contenido: str = Field(min_length=10, max_length=3500)
    duracion_min: int = Field(default=5, ge=1, le=60)
    dificultad: int = Field(default=1, ge=1, le=3)

    @field_validator("contenido")
    @classmethod
    def _html_ok(cls, v):
        return _validar_html(v)


class CapsuleUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=200)
    objetivo: str | None = Field(default=None, min_length=5, max_length=300)
    contenido: str | None = Field(default=None, min_length=10, max_length=3500)
    duracion_min: int | None = Field(default=None, ge=1, le=60)
    dificultad: int | None = Field(default=None, ge=1, le=3)

    @field_validator("contenido")
    @classmethod
    def _html_ok(cls, v):
        return v if v is None else _validar_html(v)


# ============================================================
# QUESTIONS
# ============================================================

class QuestionOut(BaseModel):
    id: int
    capsule_id: str
    topic_id: str
    tipo: str
    enunciado: str
    opciones: list[str]
    correcta: int
    retroalimentacion: str | None = None
    dificultad: int
    activo: bool

    model_config = {"from_attributes": True}


class QuestionCreate(BaseModel):
    tipo: str = Field(default="opcion_multiple")
    enunciado: str = Field(min_length=5, max_length=1000)
    opciones: list[str] = Field(min_length=2, max_length=6)
    correcta: int = Field(ge=0)
    retroalimentacion: str | None = Field(default=None, max_length=500)
    dificultad: int = Field(default=1, ge=1, le=3)

    @field_validator("tipo")
    @classmethod
    def _tipo_valido(cls, v):
        if v not in TIPOS_VALIDOS:
            raise ValueError(f"tipo debe ser uno de: {', '.join(sorted(TIPOS_VALIDOS))}")
        return v

    @field_validator("opciones")
    @classmethod
    def _opciones_ok(cls, v):
        return _validar_opciones(v)

    @field_validator("enunciado")
    @classmethod
    def _html_ok(cls, v):
        return _validar_html(v)

    @model_validator(mode="after")
    def _coherencia(self):
        if self.correcta >= len(self.opciones):
            raise ValueError(
                f"correcta={self.correcta} no existe: hay {len(self.opciones)} opciones "
                f"(índices 0 a {len(self.opciones) - 1})"
            )
        if self.tipo == "verdadero_falso" and len(self.opciones) != 2:
            raise ValueError("verdadero_falso debe tener exactamente 2 opciones")
        return self


class QuestionUpdate(BaseModel):
    enunciado: str | None = Field(default=None, min_length=5, max_length=1000)
    opciones: list[str] | None = Field(default=None, min_length=2, max_length=6)
    correcta: int | None = Field(default=None, ge=0)
    retroalimentacion: str | None = Field(default=None, max_length=500)
    dificultad: int | None = Field(default=None, ge=1, le=3)


    @field_validator("enunciado")
    @classmethod
    def _html_ok(cls, v):
        return v if v is None else _validar_html(v)

    @field_validator("opciones")
    @classmethod
    def _opciones_ok(cls, v):
        return v if v is None else _validar_opciones(v)

    @model_validator(mode="after")
    def _coherencia_parcial(self):
        # Solo se puede comprobar aquí si llegan ambos campos.
        # question_service valida con los valores finales tras mezclar con la BD.
        if self.opciones is not None and self.correcta is not None:
            if self.correcta >= len(self.opciones):
                raise ValueError(
                    f"correcta={self.correcta} no existe: hay {len(self.opciones)} "
                    f"opciones (índices 0 a {len(self.opciones) - 1})"
                )
        return self