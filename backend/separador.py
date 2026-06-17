import os
import sys
import shutil
import subprocess
import tempfile

def separar_bajo(ruta_mp3: str, directorio_destino: str) -> str:
    """
    Usa demucs para separar la pista de bajo de un MP3.
    Devuelve la ruta al archivo WAV del bajo extraído.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
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
            raise RuntimeError(f"demucs error: {resultado.stderr}")

        ruta_bajo = None
        for root, dirs, files in os.walk(tmpdir):
            for f in files:
                if "bass" in f and f.endswith(".wav"):
                    ruta_bajo = os.path.join(root, f)
                    break

        if not ruta_bajo:
            raise RuntimeError("demucs no generó el archivo de bajo")

        nombre_destino = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            directorio_destino,
            f"bajo_{os.path.basename(ruta_mp3)}.wav"
        )
        shutil.copy(ruta_bajo, nombre_destino)
        return nombre_destino