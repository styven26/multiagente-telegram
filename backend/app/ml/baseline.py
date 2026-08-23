"""Líneas base contra las que comparar el SAKT. [Ciclo 2]

Sin estas cifras, un AUC de 0.74 no significa nada: hay que demostrar que el
Transformer aporta algo sobre métodos triviales. Se evalúan exactamente sobre
las mismas ventanas de validación que usa train.py.

  1. Clase mayoritaria   : predice siempre la tasa global de aciertos
  2. Dificultad de ítem  : predice la tasa de aciertos de esa destreza
  3. Media del estudiante: aciertos previos del estudiante en esa destreza
                           (es el mismo baseline que corre hoy en el bot,
                            Mastery.fuente = 'baseline')

Uso:
    python -m app.ml.baseline --csv data/skill_builder_data.csv
"""

from __future__ import annotations

import argparse
import logging
from collections import defaultdict

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

from app.ml.dataset import (
    SecuenciasKT, cargar_assistments, dividir_por_estudiante,
)

logger = logging.getLogger(__name__)


def _metricas(nombre: str, y: list[int], p: list[float]) -> dict:
    y_arr, p_arr = np.array(y, dtype=int), np.array(p)
    pred = (p_arr >= 0.5).astype(int)
    return {
        "modelo": nombre,
        "auc": float(roc_auc_score(y_arr, p_arr)) if len(set(y)) > 1 else float("nan"),
        "accuracy": float(accuracy_score(y_arr, pred)),
        "f1": float(f1_score(y_arr, pred, zero_division=0)),
        "n": len(y),
    }


def evaluar_baselines(ventanas_entrena, ventanas_valida) -> list[dict]:
    # --- Estadísticas aprendidas SOLO del conjunto de entrenamiento ---
    aciertos_totales = sum(sum(a) for _, a in ventanas_entrena)
    n_totales = sum(len(a) for _, a in ventanas_entrena)
    tasa_global = aciertos_totales / n_totales

    por_destreza: dict[int, list[int]] = defaultdict(list)
    for destrezas, aciertos in ventanas_entrena:
        for d, a in zip(destrezas, aciertos):
            por_destreza[d].append(a)
    dificultad = {d: float(np.mean(v)) for d, v in por_destreza.items()}

    logger.info("Tasa global de aciertos (entrenamiento): %.4f", tasa_global)
    logger.info("Destrezas con estadística: %s", len(dificultad))

    y, p_mayoritaria, p_dificultad, p_estudiante = [], [], [], []

    for destrezas, aciertos in ventanas_valida:
        # Historial acumulado dentro de la propia secuencia del estudiante.
        vistos: dict[int, list[int]] = defaultdict(list)

        for d, a in zip(destrezas, aciertos):
            y.append(a)
            p_mayoritaria.append(tasa_global)
            p_dificultad.append(dificultad.get(d, tasa_global))

            previos = vistos[d]
            if previos:
                p_estudiante.append(float(np.mean(previos)))
            else:
                # Arranque en frío: sin historial, se cae a la dificultad del ítem.
                p_estudiante.append(dificultad.get(d, tasa_global))

            vistos[d].append(a)

    return [
        _metricas("Clase mayoritaria", y, p_mayoritaria),
        _metricas("Dificultad de ítem", y, p_dificultad),
        _metricas("Media del estudiante", y, p_estudiante),
    ]


def principal() -> None:
    p = argparse.ArgumentParser(description="Líneas base de Knowledge Tracing")
    p.add_argument("--csv", default="data/skill_builder_data.csv")
    p.add_argument("--largo", type=int, default=100)
    p.add_argument("--fraccion-val", type=float, default=0.2, dest="fraccion_val")
    p.add_argument("--semilla", type=int, default=42)
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    corpus = cargar_assistments(args.csv)
    entrena_sec, valida_sec = dividir_por_estudiante(
        corpus, args.fraccion_val, args.semilla)

    # Mismas ventanas que usa train.py: la comparación debe ser sobre lo mismo.
    ds_entrena = SecuenciasKT(entrena_sec, corpus.n_destrezas, args.largo)
    ds_valida = SecuenciasKT(valida_sec, corpus.n_destrezas, args.largo)

    resultados = evaluar_baselines(ds_entrena.ventanas, ds_valida.ventanas)

    print("\n" + "=" * 62)
    print(f"{'Modelo':<24}{'AUC':>9}{'Accuracy':>11}{'F1':>9}{'n':>9}")
    print("-" * 62)
    for r in resultados:
        print(f"{r['modelo']:<24}{r['auc']:>9.4f}{r['accuracy']:>11.4f}"
              f"{r['f1']:>9.4f}{r['n']:>9,}")
    print("=" * 62)


if __name__ == "__main__":
    principal()