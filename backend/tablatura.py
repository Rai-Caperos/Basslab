CUERDAS = [
    {"nombre": "E", "midi_base": 28},
    {"nombre": "A", "midi_base": 33},
    {"nombre": "D", "midi_base": 38},
    {"nombre": "G", "midi_base": 43},
]

def nota_a_tablatura(midi: int) -> dict | None:
    """
    Convierte un número MIDI a posición en el bajo.
    Prefiere cuerdas graves con traste cómodo (<=7).
    """
    candidatos = []
    for i, cuerda in enumerate(CUERDAS):
        traste = midi - cuerda["midi_base"]
        if 0 <= traste <= 12:
            candidatos.append({
                "cuerda": cuerda["nombre"],
                "cuerda_num": i + 1,
                "traste": traste,
                "midi_base": cuerda["midi_base"]
            })

    if not candidatos:
        return None

    graves = [c for c in candidatos if c["traste"] <= 7]
    if graves:
        return min(graves, key=lambda c: c["midi_base"])
    return min(candidatos, key=lambda c: c["traste"])

def construir_tablatura(notas: list[dict]) -> list[dict]:
    """
    Convierte lista de notas detectadas a tablatura con cuerdas y trastes.
    """
    tablatura = []
    for nota in notas:
        posicion = nota_a_tablatura(nota["midi"])
        if posicion:
            tablatura.append({
                "tiempo": nota["tiempo"],
                "nota": nota["nota"],
                "octava": nota["octava"],
                "cuerda": posicion["cuerda"],
                "cuerda_num": posicion["cuerda_num"],
                "traste": posicion["traste"]
            })
    return tablatura