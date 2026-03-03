import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 1. Configuración de Selenium (Modo headless para mayor velocidad)
chrome_options = Options()
# chrome_options.add_argument("--headless") # Descomenta para no ver la ventana

def verificar_contenido_bridgerton():
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
            cuerpo_texto = driver.find_element(By.TAG_NAME, "body").text.lower()
            
            # 4. Verificación de palabras clave (Bridgerton y el tema específico)
            keywords = ["bridgerton", "netflix", "lady whistledown", "regency"]
            menciona_serie = any(kw in cuerpo_texto for kw in keywords)
            menciona_busqueda = tema_busqueda in cuerpo_texto
            
            if menciona_serie and menciona_busqueda:
                status = "Relacionado"
            elif menciona_serie:
                status = "Habla de la serie, pero no del tema específico"
            else:
                status = "No relacionado"
                
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
    verificar_contenido_bridgerton()