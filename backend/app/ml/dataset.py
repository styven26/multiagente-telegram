"""Lectura y preparación de secuencias para Knowledge Tracing. [Ciclo 2]

Dos fuentes, un solo formato de salida:
  · ASSISTments 2009 (CSV público) -> validar la implementación
  · PostgreSQL (tabla responses)   -> afinar con datos propios

Formato interno: por cada estudiante, dos listas paralelas del mismo largo
    destrezas = [3, 7, 3, 1, ...]   índices enteros de la destreza
    aciertos  = [1, 0, 1, 1, ...]   0/1
ordenadas cronológicamente. Eso es todo lo que necesita el SAKT.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

logger = logging.getLogger(__name__)

LARGO_MINIMO = 3        # secuencias más cortas no aportan señal
LARGO_MAXIMO = 100      # ventana de atención del SAKT
RELLENO = 0             # índice reservado para padding


@dataclass
class Secuencia:
    estudiante: str
    destrezas: list[int]
    aciertos: list[int]

    def __len__(self) -> int:
        return len(self.destrezas)


@dataclass
class Corpus:
    secuencias: list[Secuencia]
    vocabulario: dict[str, int]      # nombre de destreza -> índice (desde 1)
    origen: str

    @property
    def n_destrezas(self) -> int:
        return len(self.vocabulario)

    def resumen(self) -> str:
        largos = [len(s) for s in self.secuencias]
        interacciones = sum(largos)
        aciertos = sum(sum(s.aciertos) for s in self.secuencias)
        return (
            f"[{self.origen}] {len(self.secuencias)} estudiantes · "
            f"{interacciones} interacciones · {self.n_destrezas} destrezas · "
            f"largo medio {np.mean(largos):.1f} (mín {min(largos)}, máx {max(largos)}) · "
            f"aciertos {aciertos / interacciones:.1%}"
        )


def _construir(df: pd.DataFrame, col_est: str, col_destreza: str,
               col_acierto: str, origen: str) -> Corpus:
    """df ya debe venir ordenado cronológicamente por estudiante."""
    nombres = sorted(df[col_destreza].astype(str).unique())
    vocabulario = {nombre: i + 1 for i, nombre in enumerate(nombres)}  # 0 = relleno

    secuencias: list[Secuencia] = []
    for estudiante, grupo in df.groupby(col_est, sort=False):
        if len(grupo) < LARGO_MINIMO:
            continue
        secuencias.append(Secuencia(
            estudiante=str(estudiante),
            destrezas=[vocabulario[str(x)] for x in grupo[col_destreza]],
            aciertos=[int(x) for x in grupo[col_acierto]],
        ))

    corpus = Corpus(secuencias, vocabulario, origen)
    logger.info(corpus.resumen())
    return corpus


def cargar_assistments(ruta: str | Path,
                       solo_originales: bool = True) -> Corpus:
    """Lee el CSV de ASSISTments 2009 (skill builder).

    solo_originales=True descarta las preguntas de andamiaje (scaffolding), que
    solo aparecen cuando el estudiante ya falló. Incluirlas sesga el modelo:
    son, por construcción, preguntas que siguen a un error.
    """
    df = pd.read_csv(ruta, encoding="latin-1", low_memory=False)
    logger.info("CSV leído: %s filas, %s columnas", len(df), len(df.columns))

    if solo_originales and "original" in df.columns:
        df = df[df["original"] == 1]

    df = df.dropna(subset=["skill_id", "user_id", "correct"])
    df = df[df["correct"].isin([0, 1])]

    # Una fila por interacción: ASSISTments duplica filas cuando un problema
    # tiene varias destrezas, y eso infla artificialmente el AUC.
    if "order_id" in df.columns:
        df = df.sort_values(["user_id", "order_id"])
        df = df.drop_duplicates(subset=["user_id", "order_id"], keep="first")

    df["skill_id"] = df["skill_id"].astype(int).astype(str)

    return _construir(df, "user_id", "skill_id", "correct", "ASSISTments 2009")


async def cargar_postgres() -> Corpus:
    """Lee la tabla responses del propio sistema."""
    from sqlalchemy import select

    from app.db.base import SessionLocal
    from app.db.models import Response

    async with SessionLocal() as s:
        filas = (await s.execute(
            select(Response.student_id, Response.topic_id, Response.es_correcta)
            .order_by(Response.student_id, Response.orden_interaccion)
        )).all()

    df = pd.DataFrame(filas, columns=["student_id", "topic_id", "es_correcta"])
    if df.empty:
        raise ValueError("La tabla responses está vacía.")
    df["es_correcta"] = df["es_correcta"].astype(int)

    return _construir(df, "student_id", "topic_id", "es_correcta", "STI local")


def dividir_por_estudiante(corpus: Corpus, fraccion_val: float = 0.2,
                           semilla: int = 42) -> tuple[list[Secuencia], list[Secuencia]]:
    """Separa entrenamiento y validación POR ESTUDIANTE, no por interacción.

    Si se dividiera por interacción, el modelo vería parte de la secuencia de un
    estudiante en entrenamiento y el resto en validación: eso es fuga de datos y
    el AUC saldría inflado. Es el error más común al reportar KT.
    """
    rng = np.random.default_rng(semilla)
    indices = rng.permutation(len(corpus.secuencias))
    corte = int(len(indices) * (1 - fraccion_val))
    entrena = [corpus.secuencias[i] for i in indices[:corte]]
    valida = [corpus.secuencias[i] for i in indices[corte:]]
    logger.info("División: %s entrenamiento / %s validación", len(entrena), len(valida))
    return entrena, valida


class SecuenciasKT(Dataset):
    """Ventanas de largo fijo para el SAKT.

    Cada muestra devuelve:
        entrada  : destreza + acierto de los pasos 0..t-1, codificados juntos
        consulta : destreza del paso t (lo que se va a predecir)
        objetivo : acierto real del paso t (0/1), o -1 donde hay relleno
    """

    def __init__(self, secuencias: list[Secuencia], n_destrezas: int,
                 largo: int = LARGO_MAXIMO):
        self.largo = largo
        self.n_destrezas = n_destrezas
        self.ventanas: list[tuple[list[int], list[int]]] = []

        for sec in secuencias:
            # Secuencias largas se trocean en ventanas sin solape.
            for i in range(0, len(sec), largo):
                d = sec.destrezas[i:i + largo]
                a = sec.aciertos[i:i + largo]
                if len(d) >= LARGO_MINIMO:
                    self.ventanas.append((d, a))

    def __len__(self) -> int:
        return len(self.ventanas)

    def __getitem__(self, idx: int):
        destrezas, aciertos = self.ventanas[idx]
        n = len(destrezas)
        relleno = self.largo - n

        # interacción = destreza + acierto * n_destrezas  (codificación del SAKT)
        interacciones = [d + a * self.n_destrezas for d, a in zip(destrezas, aciertos)]

        entrada = [RELLENO] + interacciones[:-1]      # desplazada: predice el paso t
        entrada += [RELLENO] * relleno
        consulta = destrezas + [RELLENO] * relleno
        objetivo = aciertos + [-1] * relleno          # -1 = ignorar en la pérdida

        return (
            torch.tensor(entrada, dtype=torch.long),
            torch.tensor(consulta, dtype=torch.long),
            torch.tensor(objetivo, dtype=torch.float),
        )


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ruta = sys.argv[1] if len(sys.argv) > 1 else "data/skill_builder_data.csv"

    corpus = cargar_assistments(ruta)
    entrena, valida = dividir_por_estudiante(corpus)

    ds = SecuenciasKT(entrena, corpus.n_destrezas)
    print(f"\nVentanas de entrenamiento: {len(ds)}")
    e, c, o = ds[0]
    print(f"Forma de una muestra: entrada {tuple(e.shape)}, "
          f"consulta {tuple(c.shape)}, objetivo {tuple(o.shape)}")