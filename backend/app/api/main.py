from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routers import teacher, auth

# Carpeta donde viven las imágenes que sube el docente. Fuera del código,
# para que un despliegue nuevo no las borre.
CARPETA_SUBIDAS = Path("media/uploads")
CARPETA_SUBIDAS.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="STI Multi-Agente — API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telegram descarga la imagen desde esta URL, así que debe ser pública.
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(teacher.router)
app.include_router(auth.router)


@app.get("/health")
async def health():
    return {"status": "ok"}