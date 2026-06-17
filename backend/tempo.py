import librosa

def detectar_tempo(ruta_wav: str) -> tuple[float, float]:
    """
    Detecta el tempo de un archivo WAV.
    Devuelve (bpm, segundos_por_compas).
    """
    y, sr = librosa.load(ruta_wav, mono=True)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(round(float(tempo.item()), 1))
    segundos_por_compas = round((4 * 60) / bpm, 3)
    return bpm, segundos_por_compas