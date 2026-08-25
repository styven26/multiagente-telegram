"""API del dashboard docente. [Base para el Ciclo 3]"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.api.deps import docente_actual
from app.db.base import get_session
from app.db.models import Teacher
from app.schemas.content import (
    CapsuleCreate, CapsuleOut, CapsuleUpdate,
    QuestionCreate, QuestionOut, QuestionUpdate,
    TopicCreate, TopicOut, TopicUpdate,
)
from app.schemas.metrics import ResumenDocente
from app.services import capsule_service, metrics, question_service, topic_service
from app.services.patch import SIN_CAMBIO

router = APIRouter(prefix="/api/teacher", tags=["docente"])


@router.get("/topics", response_model=list[TopicOut])
async def listar_temas(docente: Teacher = Depends(docente_actual),
                       s: AsyncSession = Depends(get_session)):
    return await topic_service.listar(s)


@router.post("/topics", response_model=TopicOut, status_code=201)
async def crear_tema(datos: TopicCreate,
                     docente: Teacher = Depends(docente_actual),
                     s: AsyncSession = Depends(get_session)):
    try:
            return await topic_service.crear(
                s, datos.nombre, datos.emoji, datos.descripcion, docente.id,
                datos.unidad, datos.prerrequisitos,
            )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch("/topics/{topic_id}", response_model=TopicOut)
async def editar_tema(topic_id: str, datos: TopicUpdate,
                      docente: Teacher = Depends(docente_actual),
                      s: AsyncSession = Depends(get_session)):
    try:
        enviados = datos.model_dump(exclude_unset=True)

        return await topic_service.actualizar(
            s, topic_id, docente.id,
            nombre=datos.nombre,
            emoji=enviados.get("emoji", SIN_CAMBIO),
            descripcion=enviados.get("descripcion", SIN_CAMBIO),
            unidad=enviados.get("unidad", SIN_CAMBIO),
            prerrequisitos=datos.prerrequisitos,
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Tema no encontrado")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/topics/{topic_id}/toggle", response_model=TopicOut)
async def alternar_tema(topic_id: str,
                        docente: Teacher = Depends(docente_actual),
                        s: AsyncSession = Depends(get_session)):
    try:
        return await topic_service.alternar_visibilidad(s, topic_id, docente.id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Tema no encontrado")

@router.get("/topics/{topic_id}/capsules", response_model=list[CapsuleOut])
async def listar_capsulas(topic_id: str,
                          docente: Teacher = Depends(docente_actual),
                          s: AsyncSession = Depends(get_session)):
    try:
        return await capsule_service.listar(s, topic_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Tema no encontrado")


@router.post("/topics/{topic_id}/capsules", response_model=CapsuleOut, status_code=201)
async def crear_capsula(topic_id: str, datos: CapsuleCreate,
                        docente: Teacher = Depends(docente_actual),
                        s: AsyncSession = Depends(get_session)):
    try:
        return await capsule_service.crear(
            s, topic_id, datos.titulo, datos.objetivo, datos.contenido,
            datos.duracion_min, datos.dificultad, docente.id,
            datos.imagen_url,
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Tema no encontrado")


@router.patch("/capsules/{capsule_id}", response_model=CapsuleOut)
async def editar_capsula(capsule_id: str, datos: CapsuleUpdate,
                         docente: Teacher = Depends(docente_actual),
                         s: AsyncSession = Depends(get_session)):
    try:
        enviados = datos.model_dump(exclude_unset=True)

        return await capsule_service.actualizar(
            s, capsule_id, docente.id, datos.titulo, datos.objetivo,
            datos.contenido, datos.duracion_min, datos.dificultad,
            imagen_url=enviados.get("imagen_url", SIN_CAMBIO),
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Cápsula no encontrada")


@router.post("/capsules/{capsule_id}/toggle", response_model=CapsuleOut)
async def alternar_capsula(capsule_id: str,
                           docente: Teacher = Depends(docente_actual),
                           s: AsyncSession = Depends(get_session)):
    try:
        return await capsule_service.alternar_visibilidad(s, capsule_id, docente.id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Cápsula no encontrada")

@router.get("/capsules/{capsule_id}/questions", response_model=list[QuestionOut])
async def listar_preguntas(capsule_id: str,
                           docente: Teacher = Depends(docente_actual),
                           s: AsyncSession = Depends(get_session)):
    try:
        return await question_service.listar(s, capsule_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Cápsula no encontrada")


@router.post("/capsules/{capsule_id}/questions", response_model=QuestionOut,
             status_code=201)
async def crear_pregunta(capsule_id: str, datos: QuestionCreate,
                         docente: Teacher = Depends(docente_actual),
                         s: AsyncSession = Depends(get_session)):
    try:
        return await question_service.crear(
            s, capsule_id, datos.tipo, datos.enunciado, datos.opciones,
            datos.correcta, datos.retroalimentacion, datos.dificultad, docente.id,
            datos.imagen_url,
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Cápsula no encontrada")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.patch("/questions/{question_id}", response_model=QuestionOut)
async def editar_pregunta(question_id: int, datos: QuestionUpdate,
                          docente: Teacher = Depends(docente_actual),
                          s: AsyncSession = Depends(get_session)):
    try:
        enviados = datos.model_dump(exclude_unset=True)

        return await question_service.actualizar(
            s, question_id, docente.id,
            tipo=datos.tipo,
            enunciado=datos.enunciado,
            opciones=datos.opciones,
            correcta=datos.correcta,
            retroalimentacion=enviados.get("retroalimentacion", SIN_CAMBIO),
            dificultad=datos.dificultad,
            imagen_url=enviados.get("imagen_url", SIN_CAMBIO),
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/questions/{question_id}/toggle", response_model=QuestionOut)
async def alternar_pregunta(question_id: int,
                            docente: Teacher = Depends(docente_actual),
                            s: AsyncSession = Depends(get_session)):
    try:
        return await question_service.alternar_visibilidad(s, question_id, docente.id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")


@router.get("/metrics/overview", response_model=ResumenDocente)
async def resumen_docente(docente: Teacher = Depends(docente_actual),
                          s: AsyncSession = Depends(get_session)):
    return await metrics.resumen(s)


CARPETA_SUBIDAS = Path("media/uploads")
TIPOS_PERMITIDOS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
TAMANO_MAX = 5 * 1024 * 1024      # 5 MB: Telegram admite más, pero pesa la carga


@router.post("/uploads", status_code=201)
async def subir_imagen(archivo: UploadFile = File(...),
                       docente: Teacher = Depends(docente_actual)):
    """Guarda una imagen y devuelve su URL pública.

    El nombre se genera aleatorio: el nombre original puede traer rutas,
    caracteres raros o colisionar con otro archivo.
    """
    extension = TIPOS_PERMITIDOS.get(archivo.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=415,
            detail="Formato no admitido. Usa PNG, JPG, WEBP o GIF.",
        )

    contenido = await archivo.read()
    if len(contenido) > TAMANO_MAX:
        raise HTTPException(
            status_code=413,
            detail="La imagen supera los 5 MB.",
        )

    CARPETA_SUBIDAS.mkdir(parents=True, exist_ok=True)
    nombre = f"{secrets.token_hex(16)}{extension}"
    (CARPETA_SUBIDAS / nombre).write_bytes(contenido)

    return {"url": f"/media/uploads/{nombre}"}