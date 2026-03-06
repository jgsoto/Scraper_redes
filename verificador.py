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
# IA VERIFICADOR
# =========================================================

load_dotenv()

class IAVerificador:

    def __init__(self):
        self.api_key = os.environ.get("GROQCLOUD_API_KEY")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        chrome_options = Options()
        self.driver = webdriver.Chrome(options=chrome_options)

    def verificar_con_ia(self, texto, serie):

        prompt = f"""
        Analiza el siguiente texto y determina si realmente habla sobre la serie "{serie}".

        Responde SOLO con:
        RELACIONADO
        PARCIAL
        NO_RELACIONADO

        Texto:
        {texto[:1000]}
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Eres analista de contenido digital."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            resultado = response.choices[0].message.content.strip().upper()

            if "RELACIONADO" in resultado and "NO" not in resultado:
                return "RELACIONADO"
            elif "PARCIAL" in resultado:
                return "PARCIAL"
            else:
                return "NO_RELACIONADO"

        except Exception as e:
            print("Error IA:", e)
            return "ERROR_IA"

    def ejecutar(self, df, serie):

        resultados = []

        for _, row in df.iterrows():

            url = row["URL"]
            print(f"🤖 Analizando: {url}")

            try:
                self.driver.get(url)

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                time.sleep(2)

                texto_total = self.driver.find_element(By.TAG_NAME, "body").text

                if len(texto_total) < 150:
                    status = "Contenido insuficiente"
                else:
                    status = self.verificar_con_ia(texto_total, serie)

            except Exception as e:
                print("Error acceso:", e)
                status = "Error en acceso"

            resultados.append(status)
            time.sleep(2)

        self.driver.quit()

        df["Resultado_Verificacion"] = resultados
        return df