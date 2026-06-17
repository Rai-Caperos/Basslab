from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import tempfile
import shutil
import os

from separador import separar_bajo
from detector import detectar_notas
from tablatura import construir_tablatura
from tempo import detectar_tempo

app = FastAPI(title="BASSLAB API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"status": "ok", "mensaje": "BASSLAB backend funcionando"}

@app.post("/analizar-bajo")
async def analizar_bajo(archivo: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_mp3 = os.path.join(tmpdir, archivo.filename)
        with open(ruta_mp3, "wb") as f:
            shutil.copyfileobj(archivo.file, f)
        destino = separar_bajo(ruta_mp3, "projects")
        return {"status": "ok", "mensaje": "Bajo extraído", "archivo_bajo": destino}

@app.post("/generar-tablatura")
async def generar_tablatura(archivo: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_wav = os.path.join(tmpdir, archivo.filename)
        with open(ruta_wav, "wb") as f:
            shutil.copyfileobj(archivo.file, f)

        notas = detectar_notas(ruta_wav)
        tablatura = construir_tablatura(notas)
        bpm, segundos_por_compas = detectar_tempo(ruta_wav)

        return {
            "status": "ok",
            "total_notas": len(tablatura),
            "tempo": bpm,
            "segundos_por_compas": segundos_por_compas,
            "tablatura": tablatura
        }

@app.get("/bajo-extraido")
def bajo_extraido(ruta: str):
    if not os.path.exists(ruta):
        return {"error": "Archivo no encontrado"}
    return FileResponse(ruta, media_type="audio/wav")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8007, reload=True)