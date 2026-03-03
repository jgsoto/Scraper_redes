from openai import OpenAI
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv

load_dotenv()
# 1. Configuración de Selenium (Modo headless para mayor velocidad)
chrome_options = Options()
# chrome_options.add_argument("--headless") # Descomenta para no ver la ventana

GROQ_API_KEY = os.environ.get("GROQCLOUD_API_KEY")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

def verificar_con_ia(texto, serie):
    try:
        prompt = f"""
        Analiza el siguiente texto y determina si realmente habla sobre la serie "{serie}".

        Responde SOLO con una de estas tres opciones exactas:
        RELACIONADO
        PARCIAL
        NO_RELACIONADO

        Texto:
        {texto[:1000]}  # Limitar a los primeros 1000 caracteres para eficiencia
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Eres un analista de contenido digital especializado en series y entretenimiento."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2  # baja creatividad, más precisión
        )

        resultado = response.choices[0].message.content.strip().upper()

        # limpieza defensiva
        if "RELACIONADO" in resultado and "NO" not in resultado:
            return "RELACIONADO"
        elif "PARCIAL" in resultado:
            return "PARCIAL"
        else:
            return "NO_RELACIONADO"

    except Exception as e:
        print(f"Error IA: {e}")
        return "ERROR_IA"

def verificar_contenido():
    # 2. Cargar el Excel
    try:
        df = pd.read_excel('paginas_encontradas.xlsx')
    except FileNotFoundError:
        print("Error: No se encontró el archivo Excel.")
        return

    # Inicializar el Driver (Asegúrate de tener el path correcto o usar webdriver-manager)
    driver = webdriver.Chrome(options=chrome_options)
    
    resultados = []

    for index, row in df.iterrows():
        url = row['URL']
        tema_busqueda = str(row['Busqueda']).lower()
        
        print(f"Analizando: {url}")
        
        try:
            driver.get(url)
            
            # Esperar a que el cuerpo de la página cargue
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 3. Extraer el texto visible de la publicación
            # Nota: Dependiendo de la red social, podrías necesitar un selector más específico
            # Scroll para cargar contenido dinámico
            for _ in range(2):
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1.5)

            texto_total = ""

            # 1️⃣ Meta description (muy confiable)
            try:
                meta = driver.find_element(By.XPATH, "//meta[@name='description']")
                texto_total += meta.get_attribute("content") + " "
            except:
                pass

            # 2️⃣ Título principal (YouTube / general)
            try:
                titulo = driver.find_element(By.TAG_NAME, "h1").text
                texto_total += titulo + " "
            except:
                pass

            # 3️⃣ Descripción YouTube específica
            if "youtube.com" in url:
                try:
                    descripcion = driver.find_element(By.ID, "description").text
                    texto_total += descripcion + " "
                except:
                    pass

            # 4️⃣ Body como fallback final
            try:
                body = driver.find_element(By.TAG_NAME, "body").text
                texto_total += body
            except:
                pass

            texto_total = texto_total.strip()

            if len(texto_total) < 150:
                status = "Contenido insuficiente"
            else:
                status = verificar_con_ia(texto_total, "agatha christie: las siete esferas")
                     
            resultados.append(status)
            
        except Exception as e:
            print(f"Error al acceder a {url}: {e}")
            resultados.append("Error en acceso")
        
        time.sleep(2) # Pausa cortés para evitar bloqueos

    # 5. Guardar resultados de vuelta al Excel
    df['Resultado_Verificacion'] = resultados
    df.to_excel('publicaciones_verificadas.xlsx', index=False)
    print("Proceso terminado. Archivo guardado como 'publicaciones_verificadas.xlsx'")
    
    driver.quit()

if __name__ == "__main__":
    verificar_contenido()