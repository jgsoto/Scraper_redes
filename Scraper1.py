from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import random
from urllib.parse import quote_plus

# ----------------------
# FUNCIÓN FILTRO MEJORADA
# ----------------------

def es_pagina_valida(url, titulo_serie):
    if not url:
        return False

    # Evitar enlaces internos de Google
    if any(x in url for x in ["google.com", "google.com.ec", "support.google", "accounts.google"]):
        return False

    # Redes sociales y plataformas de streaming
    sitios_relevantes = [
        "instagram.com", "facebook.com", "tiktok.com", 
        "youtube.com", "x.com", "twitter.com", "netflix.com"
    ]

    # El enlace debe ser de un sitio relevante
    es_sitio_objetivo = any(sitio in url.lower() for sitio in sitios_relevantes)
    
    return es_sitio_objetivo

# ----------------------
# CONFIGURACIÓN
# ----------------------

serie = "El Botín"
plataforma = "Netflix"

# Añadimos Netflix a las consultas para forzar resultados de la plataforma
queries = [
    f'"{serie}" {plataforma} Uruguay site:instagram.com',
    f'"{serie}" {plataforma} Uruguay site:facebook.com',
    f'"{serie}" {plataforma} Uruguay site:tiktok.com',
    f'"{serie}" {plataforma} Uruguay site:netflix.com', # Nueva búsqueda específica
    f'"{serie}" {plataforma} Uruguay site:x.com'
]

max_paginas = 2

# ----------------------
# DRIVER CON MODO INCÓGNITO
# ----------------------

options = webdriver.ChromeOptions()
options.add_argument("--incognito") # <--- ACTIVAR MODO INCÓGNITO
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
        time.sleep(random.uniform(5, 8)) # Pausas un poco más largas para mayor seguridad

        # Capturamos los contenedores de resultados para ser más precisos
        enlaces = driver.find_elements(By.CSS_SELECTOR, "div.g a") 

        for link in enlaces:
            url = link.get_attribute("href")
            
            if es_pagina_valida(url, serie):
                resultados.append({
                    "Serie": serie,
                    "Plataforma": plataforma,
                    "Busqueda": query,
                    "URL": url
                })

        print(f"Página {pagina + 1} completada")
        time.sleep(random.uniform(3, 5))

driver.quit()

# ----------------------
# GUARDAR RESULTADOS
# ----------------------

df = pd.DataFrame(resultados)
df = df.drop_duplicates(subset=["URL"]) # Evitar URLs repetidas

df.to_excel("resultados_netflix_uruguay.xlsx", index=False)
print(f"Proceso finalizado. Se encontraron {len(df)} enlaces únicos. ✅")