# utils.py

import os

ARCHIVO_PROCESADAS = "procesadas.txt"

def cargar_urls_procesadas():
    if not os.path.exists(ARCHIVO_PROCESADAS):
        return set()

    with open(ARCHIVO_PROCESADAS, "r") as f:
        return set(line.strip() for line in f)


def guardar_urls_procesadas(urls):
    with open(ARCHIVO_PROCESADAS, "a") as f:
        for url in urls:
            f.write(url + "\n")