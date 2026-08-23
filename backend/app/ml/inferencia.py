"""Inferencia del SAKT en producción. [Ciclo 2]

Carga un checkpoint una sola vez y predice P(acierto) antes de que el estudiante
responda. Cada predicción queda en model_predictions con su resultado real, que
es lo que permite calcular el AUC **en producción**, no solo en validación.

Si no hay checkpoint configurado, o si el vocabulario del modelo no cubre los
temas locales, el motor se declara no disponible y el sistema sigue con el
baseline. Nunca inventa una predicción.
"""

from __future__ import annotations

import logging
from pathlib import Path

import torch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import ModelRun, Response
from app.ml.sakt import SAKT

logger = logging.getLogger(__name__)


class MotorKT:
    """Singleton perezoso: el modelo se carga en el primer uso."""

    def __init__(self) -> None:
        self.modelo: SAKT | None = None
        self.vocabulario: dict[str, int] = {}
        self.largo: int = 50
        self.version: str | None = None
        self.model_run_id: int | None = None
        self._intentado = False

    @property
    def disponible(self) -> bool:
        return self.modelo is not None

    def cargar(self) -> bool:
        if self._intentado:
            return self.disponible
        self._intentado = True

        ruta = settings.SAKT_CHECKPOINT
        if not ruta or not Path(ruta).exists():
            logger.info("Sin checkpoint de SAKT: se usará el baseline.")
            return False

        try:
            datos = torch.load(ruta, map_location="cpu", weights_only=False)
            hp = datos["hiperparametros"]

            modelo = SAKT(
                n_destrezas=hp["n_destrezas"], d_modelo=hp["d_modelo"],
                n_cabezas=hp["cabezas"], largo_max=hp["largo"],
                dropout=hp["dropout"],
            )
            modelo.load_state_dict(datos["estado"])
            modelo.eval()

            self.modelo = modelo
            self.vocabulario = datos["vocabulario"]
            self.largo = hp["largo"]
            self.version = datos.get("version")
            logger.info("SAKT cargado (%s destrezas, ventana %s, versión %s)",
                        hp["n_destrezas"], self.largo, self.version)
            return True
        except Exception:                                # noqa: BLE001
            logger.exception("No se pudo cargar el checkpoint de SAKT")
            self.modelo = None
            return False

    async def _resolver_model_run(self, s: AsyncSession) -> int | None:
        if self.model_run_id is not None or self.version is None:
            return self.model_run_id
        self.model_run_id = await s.scalar(
            select(ModelRun.id).where(ModelRun.version == self.version,
                                      ModelRun.tipo == "sakt")
        )
        if self.model_run_id is None:
            logger.warning("El checkpoint %s no tiene fila en model_runs; "
                           "no se registrarán predicciones.", self.version)
        return self.model_run_id

    async def predecir(self, s: AsyncSession, student_id: int,
                       topic_id: str) -> float | None:
        """P(acierto) del estudiante en la siguiente pregunta de `topic_id`."""
        if not self.cargar():
            return None
        if topic_id not in self.vocabulario:
            return None                      # tema fuera del vocabulario entrenado

        historial = (await s.execute(
            select(Response.topic_id, Response.es_correcta)
            .where(Response.student_id == student_id)
            .order_by(Response.orden_interaccion)
        )).all()

        destrezas, aciertos = [], []
        for t, ok in historial:
            if t in self.vocabulario:        # se ignora lo que el modelo no conoce
                destrezas.append(self.vocabulario[t])
                aciertos.append(int(ok))

        n = len(self.vocabulario)
        interacciones = [d + a * n for d, a in zip(destrezas, aciertos)]

        # La consulta es el paso a predecir; la entrada va desplazada un lugar.
        consulta = destrezas + [self.vocabulario[topic_id]]
        entrada = [0] + interacciones

        # Se conserva lo más reciente y se rellena por la izquierda.
        consulta = consulta[-self.largo:]
        entrada = entrada[-self.largo:]
        relleno = self.largo - len(consulta)
        consulta = [0] * relleno + consulta
        entrada = [0] * relleno + entrada

        with torch.no_grad():
            logits = self.modelo(
                torch.tensor([entrada], dtype=torch.long),
                torch.tensor([consulta], dtype=torch.long),
            )
        return float(torch.sigmoid(logits[0, -1]).item())


motor = MotorKT()