"""Registra en model_runs los checkpoints del SAKT entrenados sobre ASSISTments.

Cada checkpoint guarda sus hiperparámetros y métricas; este script los lee del
archivo en vez de copiarlos a mano, así la fila de la base y el modelo en disco
no pueden desincronizarse. Es idempotente: reejecutarlo no duplica filas.

Uso:
    python -m scripts.registrar_checkpoints
"""

import asyncio
import glob
from pathlib import Path

import torch
from sqlalchemy import select

from app.db.base import SessionLocal
from app.db.models import ModelRun

CARPETA = "models"


async def principal() -> None:
    archivos = sorted(glob.glob(f"{CARPETA}/*.pt"))
    if not archivos:
        print(f"No hay checkpoints en {CARPETA}/")
        return

    async with SessionLocal() as s:
        for ruta in archivos:
            version = Path(ruta).stem

            existente = await s.scalar(
                select(ModelRun).where(ModelRun.version == version)
            )
            if existente is not None:
                print(f"  ya existe  {version}")
                continue

            datos = torch.load(ruta, map_location="cpu", weights_only=False)
            hp = datos.get("hiperparametros", {})
            m = datos.get("metricas", {})

            s.add(ModelRun(
                ciclo=2,
                tipo="sakt",
                nombre_modelo="SAKT",
                version=version,
                dataset="assistments_2009_skill_builder",
                descripcion=(
                    f"SAKT sobre ASSISTments 2009: ventana {hp.get('largo')}, "
                    f"d_modelo {hp.get('d_modelo')}, {hp.get('cabezas')} cabezas, "
                    f"dropout {hp.get('dropout')}. Division por estudiante "
                    f"(3072 entrenamiento / 769 validacion), semilla "
                    f"{hp.get('semilla')}."
                ),
                hiperparametros=hp,
                metricas=m,
                auc=m.get("auc"),
                f1=m.get("f1"),
                accuracy=m.get("accuracy"),
                precision=m.get("precision"),
                recall=m.get("recall"),
            ))
            print(f"  registrado {version}  AUC={m.get('auc'):.4f}")

        await s.commit()

    print("\nListo.")


if __name__ == "__main__":
    asyncio.run(principal())