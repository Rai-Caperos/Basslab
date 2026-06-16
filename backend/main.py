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
    
@app.post("/detectar-notas")
async def detectar_notas(archivo: UploadFile = File(...)):
    import librosa
    import numpy as np

    NOTAS_ES = ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]

    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_wav = os.path.join(tmpdir, archivo.filename)
        with open(ruta_wav, "wb") as f:
            shutil.copyfileobj(archivo.file, f)

        y, sr = librosa.load(ruta_wav, mono=True)

        # Detectar frecuencias fundamentales con piptrack
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, threshold=0.1)

        notas_detectadas = []
        for t in range(0, pitches.shape[1], 10):  # cada 10 frames ~0.2 segundos
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 30 and pitch < 400:  # rango del bajo: 30Hz-400Hz
                nota_midi = librosa.hz_to_midi(pitch)
                nota_idx = int(round(nota_midi)) % 12
                octava = int(round(nota_midi)) // 12 - 1
                nombre = NOTAS_ES[nota_idx]
                notas_detectadas.append({
                    "tiempo": round(t * 512 / sr, 2),
                    "nota": nombre,
                    "octava": octava,
                    "frecuencia_hz": round(float(pitch), 2)
                })

        return {
            "status": "ok",
            "total_notas": len(notas_detectadas),
            "notas": notas_detectadas[:50]  # primeras 50 para no saturar
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8007, reload=True)