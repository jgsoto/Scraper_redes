import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# 1. Configuración de Chrome
chrome_options = Options()
# chrome_options.add_argument("--headless") 
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def extraer_perfil():
    # Leer el archivo Excel
    archivo_excel = 'paginas_encontradas.xlsx' 
    df = pd.read_excel(archivo_excel)
    
    perfiles_extraidos = []

    for index, fila in df.iterrows():
        url = str(fila['URL']).lower() # Convertimos a minúsculas para comparar mejor
        
        # --- FILTRO DE INSTAGRAM ---
        if "instagram.com" not in url:
            print(f"Saltando ({index + 1}): No es una URL de Instagram -> {url}")
            perfiles_extraidos.append("No es Instagram")
            continue 
        # ---------------------------

        print(f"Procesando ({index + 1}/{len(df)}): {url}")
        
        try:
            driver.get(url)
            
            # Esperar a que el elemento del perfil sea visible
            # Se usan varios selectores comunes por si Instagram cambia las clases
            espera = WebDriverWait(driver, 12)
            
            # Selector específico para el nombre de usuario en el encabezado del post
            selector_perfil = "header a.x1i10hfl, a._a6hd, h2._aacl"
            
            elemento_perfil = espera.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector_perfil))
            )
            
            username = elemento_perfil.text
            
            # Si el texto está vacío (a veces pasa por carga lenta), intentamos otro atributo
            if not username:
                username = elemento_perfil.get_attribute("title")

            perfiles_extraidos.append(username)
            print(f"Encontrado: {username}")
            
        except Exception as e:
            print(f"No se pudo extraer el perfil de {url}. Posible bloqueo o sesión requerida.")
            perfiles_extraidos.append("Error / Requiere Login")
        
        # Pausa para no saturar al servidor
        time.sleep(3)

    # Añadir los resultados al DataFrame y guardar
    df['Perfil_Publicador'] = perfiles_extraidos
    df.to_excel('resultados_perfiles_instagram.xlsx', index=False)
    print("\nProceso terminado. Archivo 'resultados_perfiles_instagram.xlsx' generado.")

if __name__ == "__main__":
    try:
        extraer_perfil()
    finally:
        driver.quit()