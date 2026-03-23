from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

# =========================================================
# CONFIG
# =========================================================
load_dotenv()

class IAVerificador:

    def __init__(self):
        self.api_key = os.environ.get("GROQCLOUD_API_KEY")

        if not self.api_key:
            raise ValueError("❌ No se encontró GROQCLOUD_API_KEY en .env")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(options=chrome_options)

    # =========================================================
    # IA
    # =========================================================
    def verificar_con_ia(self, texto, tema):

        prompt = f"""
            Analiza el siguiente texto y determina si está relacionado con el estado de Baja California, México.

            Incluye referencias a ciudades como:
            - Tijuana
            - Mexicali
            - Ensenada
            - Tecate
            - Rosarito  

            Responde SOLO con una de estas opciones:
            RELACIONADO_BAJA_CALIFORNIA
            PARCIAL
            NO_RELACIONADO

            Texto:
            {texto[:1000]}
            """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Eres un analista de contenido geográfico."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            resultado = response.choices[0].message.content.strip().upper()

            # 🔥 Normalización robusta
            if "RELACIONADO_BAJA_CALIFORNIA" in resultado:
                return "RELACIONADO_BAJA_CALIFORNIA"
            elif "PARCIAL" in resultado:
                return "PARCIAL"
            elif "NO" in resultado:
                return "NO_RELACIONADO"
            else:
                return "NO_RELACIONADO"

        except Exception as e:
            print("❌ Error IA:", e)
            return "ERROR_IA"

    # =========================================================
    # EJECUCIÓN
    # =========================================================
    def ejecutar(self, df, tema):

        resultados = []

        # 🔥 Palabras clave para pre-filtrado (ahorra IA)
        lugares_bc = [
            "tijuana", "mexicali", "ensenada",
            "tecate", "rosarito"
        ]

        for _, row in df.iterrows():

            url = row["URL"]
            print(f"🔍 Analizando: {url}")

            try:
                self.driver.get(url)

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                time.sleep(2)

                texto_total = self.driver.find_element(By.TAG_NAME, "body").text.lower()

                # =====================================================
                # VALIDACIONES
                # =====================================================
                if len(texto_total) < 150:
                    status = "CONTENIDO_INSUFICIENTE"

                # 🔥 FILTRO RÁPIDO (ANTES DE IA)
                elif not any(lugar in texto_total for lugar in lugares_bc):
                    status = "NO_RELACIONADO"

                else:
                    status = self.verificar_con_ia(texto_total, tema)

            except Exception as e:
                print(f"❌ Error acceso: {e}")
                status = "ERROR_ACCESO"

            resultados.append(status)
            time.sleep(2)

        self.driver.quit()

        df["Resultado_Verificacion"] = resultados
        return df