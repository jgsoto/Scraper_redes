from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import random
from urllib.parse import quote_plus

# ----------------------
# FUNCIÓN FILTRO
# ----------------------

def es_pagina_valida(url):
    if not url:
        return False

    if "google.com/search" in url:
        return False

    redes = [
        "instagram.com",
        "facebook.com",
        "tiktok.com",
        "youtube.com",
        "x.com",
        "twitter.com"
    ]

    return any(red in url for red in redes)

# ----------------------
# CONFIGURACIÓN
# ----------------------

serie = "El Botín"

queries = [
    f'"{serie}" Uruguay site:instagram.com',
    f'"{serie}" Uruguay site:facebook.com',
    f'"{serie}" Uruguay site:tiktok.com',
    f'"{serie}" Uruguay site:youtube.com',
    f'"{serie}" Uruguay site:x.com'
]

max_paginas = 3

# ----------------------
# DRIVER
# ----------------------

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

resultados = []

# ----------------------
# BÚSQUEDA
# ----------------------

for query in queries:

    print(f"Buscando: {query}")

    query_encoded = quote_plus(query)

    for pagina in range(max_paginas):

        start = pagina * 10

        url_busqueda = f"https://www.google.com/search?q={query_encoded}&start={start}"

        driver.get(url_busqueda)

        time.sleep(random.uniform(4, 7))

        links = driver.find_elements(By.XPATH, "//a")

        for link in links:
            url = link.get_attribute("href")

            if es_pagina_valida(url):
                resultados.append({
                    "Serie": serie,
                    "Busqueda": query,
                    "URL": url
                })

        print(f"Página {pagina + 1} completada")

        time.sleep(random.uniform(3, 6))

driver.quit()

# ----------------------
# GUARDAR RESULTADOS
# ----------------------

df = pd.DataFrame(resultados)
df = df.drop_duplicates()

df.to_excel("paginas_encontradas.xlsx", index=False)

print("Búsqueda completada ✅")