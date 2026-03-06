from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import random
from urllib.parse import quote_plus

class GoogleScraper:

    def __init__(self, serie, max_paginas=3):
        self.serie = serie
        self.max_paginas = max_paginas
        self.driver = self._configurar_driver()
        self.resultados = []

    def _configurar_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        return driver

    def es_pagina_valida(self, url):
        if not url:
            return False

        if "google.com/" in url:
            return False

        redes = [
            "instagram.com",
            "facebook.com",
            "tiktok.com",
            "youtube.com",
            "x.com",
            "twitter.com",
        ]

        return any(red in url for red in redes)

    def ejecutar(self):

        queries = [
            f'"{self.serie}" Netflix Argentina site:instagram.com',
            f'"{self.serie}" Netflix Argentina site:facebook.com',
            f'"{self.serie}" Netflix Argentina site:tiktok.com',
            f'"{self.serie}" Netflix Argentina site:youtube.com',
            f'"{self.serie}" Netflix Argentina site:x.com',
        ]

        try:
            for query in queries:
                print(f"\n🔎 Buscando: {query}")
                query_encoded = quote_plus(query)

                for pagina in range(self.max_paginas):

                    start = pagina * 10
                    url_busqueda = f"https://www.google.com/search?q={query_encoded}&start={start}"

                    self.driver.get(url_busqueda)
                    time.sleep(random.uniform(4, 7))

                    links = self.driver.find_elements(By.XPATH, "//a")

                    for link in links:
                        url = link.get_attribute("href")

                        if self.es_pagina_valida(url):
                            self.resultados.append({
                                "Serie": self.serie,
                                "Busqueda": query,
                                "URL": url
                            })

                    print(f"   ✅ Página {pagina + 1}")

                    time.sleep(random.uniform(3, 6))

        finally:
            self.driver.quit()

        return pd.DataFrame(self.resultados).drop_duplicates()