from basic_pitch.inference import predict

NOTAS_ES = ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]

# Rango real del bajo: Mi1 (MIDI 28) a Re3 (MIDI 50)
MIDI_MIN = 28
MIDI_MAX = 50
VELOCIDAD_MIN = 0.2
VENTANA_ARMONICO = 0.3

def detectar_notas(ruta_wav: str) -> list[dict]:
    """
    Usa Basic Pitch para detectar notas en un WAV.
    Filtra armónicos y devuelve lista ordenada por tiempo.
    """
    _, _, note_events = predict(ruta_wav)
    note_events = sorted(note_events, key=lambda n: n[0])

    # Filtrar por rango y velocidad
    note_events = [
        n for n in note_events
        if MIDI_MIN <= int(n[2]) <= MIDI_MAX and float(n[3]) >= VELOCIDAD_MIN
    ]

    # Filtrar armónicos — si hay nota X y nota X-12 cercana, X es armónico
    notas_filtradas = []
    for note in note_events:
        midi = int(note[2])
        tiempo = float(note[0])
        es_armonico = any(
            int(other[2]) == midi - 12 or int(other[2]) == midi - 24
            for other in note_events
            if abs(float(other[0]) - tiempo) < VENTANA_ARMONICO
        )
        if not es_armonico:
            notas_filtradas.append(note)

    # Convertir a diccionarios
    notas = []
    nota_anterior = None
    for note in notas_filtradas:
        tiempo = round(float(note[0]), 2)
        midi = int(note[2])
        nota_idx = midi % 12
        octava = midi // 12 - 1
        nombre = NOTAS_ES[nota_idx]

        clave = f"{nombre}{octava}"
        if clave == nota_anterior:
            continue
        nota_anterior = clave

        notas.append({
            "tiempo": tiempo,
            "nota": nombre,
            "octava": octava,
            "midi": midi
        })

    return notas