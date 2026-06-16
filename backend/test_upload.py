import requests

ruta = r"G:\Musica\Pop Movida 80's\1978-80\80 Los Bólidos - Ráfagas.mp3"

with open(ruta, "rb") as f:
    r = requests.post(
        "http://127.0.0.1:8007/analizar-bajo",
        files={"archivo": f}
    )
    print(r.json())