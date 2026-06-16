from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import tempfile
import shutil
import os
import subprocess

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
    # Guardar el MP3 en un directorio temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_mp3 = os.path.join(tmpdir, archivo.filename)
        with open(ruta_mp3, "wb") as f:
            shutil.copyfileobj(archivo.file, f)

        # Ejecutar demucs sobre el archivo
        import sys
        resultado = subprocess.run(
            [
                sys.executable, "-m", "demucs",
                "--two-stems", "bass",
                "-o", tmpdir,
                ruta_mp3
            ],
            capture_output=True,
            text=True
        )

        if resultado.returncode != 0:
            return {"error": resultado.stderr}

        # Buscar el archivo de bajo generado
        ruta_bajo = None
        for root, dirs, files in os.walk(tmpdir):
            for f in files:
                if "bass" in f and f.endswith(".wav"):
                    ruta_bajo = os.path.join(root, f)
                    break

        if not ruta_bajo:
            return {"error": "demucs no generó el archivo de bajo"}

        # Copiar el bajo a la carpeta projects
        destino = os.path.join("projects", f"bajo_{archivo.filename}.wav")
        shutil.copy(ruta_bajo, destino)

        return {
            "status": "ok",
            "mensaje": "Bajo extraído correctamente",
            "archivo_bajo": destino
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8007, reload=True)