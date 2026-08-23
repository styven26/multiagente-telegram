"""Entrenamiento y evaluación del SAKT. [Ciclo 2]

Cada ejecución queda registrada en la tabla model_runs con sus hiperparámetros
y sus métricas. Esa trazabilidad es lo que permite defender en la tesis qué
modelo produjo qué número, y reproducirlo.

Uso:
    python -m app.ml.train --csv data/skill_builder_data.csv --epocas 20
    python -m app.ml.train --fuente postgres --epocas 30
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, roc_auc_score,
)
from torch.utils.data import DataLoader

from app.ml.dataset import (
    SecuenciasKT, cargar_assistments, cargar_postgres, dividir_por_estudiante,
)
from app.ml.sakt import SAKT, perdida_enmascarada

logger = logging.getLogger(__name__)
CARPETA_MODELOS = Path("models")


def evaluar(modelo: SAKT, cargador: DataLoader, dispositivo: str) -> dict:
    modelo.eval()
    probabilidades, reales, perdidas = [], [], []

    with torch.no_grad():
        for entrada, consulta, objetivo in cargador:
            entrada = entrada.to(dispositivo)
            consulta = consulta.to(dispositivo)
            objetivo = objetivo.to(dispositivo)

            logits = modelo(entrada, consulta)
            perdidas.append(perdida_enmascarada(logits, objetivo).item())

            valido = objetivo >= 0
            probabilidades.extend(torch.sigmoid(logits[valido]).cpu().numpy())
            reales.extend(objetivo[valido].cpu().numpy())

    y = np.array(reales, dtype=int)
    p = np.array(probabilidades)
    pred = (p >= 0.5).astype(int)

    return {
        "perdida": float(np.mean(perdidas)),
        "auc": float(roc_auc_score(y, p)) if len(set(y)) > 1 else float("nan"),
        "accuracy": float(accuracy_score(y, pred)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "n": int(len(y)),
    }


async def registrar_ejecucion(corpus_origen: str, hiperparametros: dict,
                              metricas: dict, version: str) -> int | None:
    """Deja constancia en model_runs. Si la BD no está, no rompe el entrenamiento."""
    try:
        from app.db.base import SessionLocal, engine
        from app.db.models import ModelRun

        async with SessionLocal() as s:
            ejecucion = ModelRun(
                ciclo=2, tipo="sakt", nombre_modelo="SAKT",
                version=version, dataset=corpus_origen,
                descripcion="Self-Attentive Knowledge Tracing, 1 capa",
                hiperparametros=hiperparametros,
                metricas=metricas,
                auc=metricas.get("auc"),
                f1=metricas.get("f1"),
                accuracy=metricas.get("accuracy"),
                precision=metricas.get("precision"),
                recall=metricas.get("recall"),
                fecha_entrenamiento=datetime.now(timezone.utc),
                activo=True,
            )
            s.add(ejecucion)
            await s.commit()
            await s.refresh(ejecucion)
            identificador = ejecucion.id

        await engine.dispose()
        return identificador
    except Exception as e:                               # noqa: BLE001
        logger.warning("No se pudo registrar en model_runs: %s", e)
        return None


def entrenar(args) -> None:
    torch.manual_seed(args.semilla)
    np.random.seed(args.semilla)
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("Dispositivo: %s", dispositivo)

    # --- Datos ---
    if args.fuente == "postgres":
        corpus = asyncio.run(cargar_postgres())
    else:
        corpus = cargar_assistments(args.csv)

    entrena_sec, valida_sec = dividir_por_estudiante(
        corpus, args.fraccion_val, args.semilla)

    ds_entrena = SecuenciasKT(entrena_sec, corpus.n_destrezas, args.largo)
    ds_valida = SecuenciasKT(valida_sec, corpus.n_destrezas, args.largo)
    logger.info("Ventanas: %s entrenamiento, %s validación",
                len(ds_entrena), len(ds_valida))

    cargador_entrena = DataLoader(ds_entrena, batch_size=args.lote, shuffle=True)
    cargador_valida = DataLoader(ds_valida, batch_size=args.lote)

    # --- Modelo ---
    modelo = SAKT(corpus.n_destrezas, args.d_modelo, args.cabezas,
                  args.largo, args.dropout).to(dispositivo)
    optimizador = torch.optim.AdamW(modelo.parameters(), lr=args.lr,
                                    weight_decay=args.weight_decay)

    mejor_auc, mejor_estado, sin_mejora = -1.0, None, 0

    for epoca in range(1, args.epocas + 1):
        modelo.train()
        perdidas = []
        for entrada, consulta, objetivo in cargador_entrena:
            entrada = entrada.to(dispositivo)
            consulta = consulta.to(dispositivo)
            objetivo = objetivo.to(dispositivo)

            optimizador.zero_grad()
            perdida = perdida_enmascarada(modelo(entrada, consulta), objetivo)
            perdida.backward()
            torch.nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
            optimizador.step()
            perdidas.append(perdida.item())

        m = evaluar(modelo, cargador_valida, dispositivo)
        logger.info(
            "Época %2d | entrena %.4f | valida %.4f | AUC %.4f | acc %.4f | F1 %.4f",
            epoca, float(np.mean(perdidas)), m["perdida"], m["auc"],
            m["accuracy"], m["f1"],
        )

        if m["auc"] > mejor_auc:
            mejor_auc, mejor_metricas = m["auc"], m
            mejor_estado = {k: v.cpu().clone() for k, v in modelo.state_dict().items()}
            sin_mejora = 0
        else:
            sin_mejora += 1
            if sin_mejora >= args.paciencia:
                logger.info("Parada temprana en la época %s", epoca)
                break

    # --- Guardado ---
    CARPETA_MODELOS.mkdir(exist_ok=True)
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = CARPETA_MODELOS / f"sakt_{args.fuente}_{version}.pt"

    hiperparametros = {
        "d_modelo": args.d_modelo, "cabezas": args.cabezas, "largo": args.largo,
        "dropout": args.dropout, "lr": args.lr, "lote": args.lote,
        "weight_decay": args.weight_decay, "epocas_max": args.epocas,
        "semilla": args.semilla, "n_destrezas": corpus.n_destrezas,
    }

    torch.save({
        "version": version,
        "estado": mejor_estado,
        "vocabulario": corpus.vocabulario,
        "hiperparametros": hiperparametros,
        "metricas": mejor_metricas,
    }, ruta)

    print("\n" + "=" * 60)
    print(f"Modelo guardado en {ruta}")
    print(f"Dataset : {corpus.origen}")
    print(f"AUC     : {mejor_metricas['auc']:.4f}")
    print(f"Accuracy: {mejor_metricas['accuracy']:.4f}")
    print(f"F1      : {mejor_metricas['f1']:.4f}")
    print(f"n       : {mejor_metricas['n']:,} predicciones evaluadas")
    print("=" * 60)

    identificador = asyncio.run(registrar_ejecucion(
        corpus.origen, hiperparametros, mejor_metricas, version))
    if identificador:
        print(f"Registrado en model_runs con id={identificador}")


def principal() -> None:
    p = argparse.ArgumentParser(description="Entrena el SAKT")
    p.add_argument("--fuente", choices=["assistments", "postgres"],
                   default="assistments")
    p.add_argument("--csv", default="data/skill_builder_data.csv")
    p.add_argument("--epocas", type=int, default=20)
    p.add_argument("--lote", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--weight-decay", type=float, default=1e-5, dest="weight_decay")
    p.add_argument("--d-modelo", type=int, default=128, dest="d_modelo")
    p.add_argument("--cabezas", type=int, default=8)
    p.add_argument("--largo", type=int, default=100)
    p.add_argument("--dropout", type=float, default=0.2)
    p.add_argument("--paciencia", type=int, default=5)
    p.add_argument("--fraccion-val", type=float, default=0.2, dest="fraccion_val")
    p.add_argument("--semilla", type=int, default=42)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    entrenar(p.parse_args())


if __name__ == "__main__":
    principal()