from basic_pitch.inference import predict

NOTAS_ES = ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]

# Rango real del bajo: Mi1 (MIDI 28) a Re3 (MIDI 50)
MIDI_MIN = 28
MIDI_MAX = 50
VELOCIDAD_MIN = 0.25
VENTANA_ARMONICO = 0.3

def detectar_notas(ruta_wav: str) -> list[dict]:
    """
    Usa Basic Pitch para detectar notas en un WAV.
    Filtra armónicos y devuelve lista ordenada por tiempo.
    """
    _, _, note_events = predict(
        ruta_wav,
        onset_threshold=0.3,
        frame_threshold=0.2,
        minimum_note_length=60
    )
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
    tiempo_anterior = 0
    for note in notas_filtradas:
        tiempo = round(float(note[0]), 2)
        midi = int(note[2])
        nota_idx = midi % 12
        octava = midi // 12 - 1
        nombre = NOTAS_ES[nota_idx]

        clave = f"{nombre}{octava}"
        if clave == nota_anterior and (tiempo - tiempo_anterior) < 0.25:
            continue
        nota_anterior = clave
        tiempo_anterior = tiempo

        # Corregir offset de un semitono — Basic Pitch detecta consistentemente un semitono alto
        midi_corregido = midi - 1
        if midi_corregido < MIDI_MIN:
            continue
        nota_idx_c = midi_corregido % 12
        octava_c = midi_corregido // 12 - 1
        nombre_c = NOTAS_ES[nota_idx_c]

        notas.append({
            "tiempo": tiempo,
            "nota": nombre_c,
            "octava": octava_c,
            "midi": midi_corregido
        })

    return notas