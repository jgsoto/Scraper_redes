import json
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 1. DEFINICIÓN DE LA CLASE (Debe ir arriba) ---
class InstagramSession:
    def __init__(self, driver, cookie_file="instagram_cookies.json"):
        self.driver = driver
        self.cookie_file = cookie_file

    def save_cookies(self):
        print("\n[!] ESPERA: Inicia sesión manualmente en la ventana del navegador.")
        input("Una vez que veas tu feed de Instagram, presiona ENTER aquí para guardar la sesión...")
        with open(self.cookie_file, "w") as file:
            json.dump(self.driver.get_cookies(), file)
        print("✅ Cookies guardadas correctamente.")

    def load_cookies(self):
        if os.path.exists(self.cookie_file):
            # Instagram requiere estar en su dominio antes de inyectar cookies
            self.driver.get("https://www.instagram.com/robots.txt") 
            with open(self.cookie_file, "r") as file:
                cookies = json.load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            self.driver.refresh()
            print("✅ Sesión cargada desde cookies.")
            return True
        return False

# --- 2. FUNCIÓN DE PROCESAMIENTO ---
def verificar_instagram_bridgerton():
    try:
        df = pd.read_excel('resultados_instagram.xlsx')
    except Exception as e:
        print(f"Error al leer el Excel: {e}")
        return

    df_ig = df[df['URL'].str.contains("instagram.com", na=False)].copy()

    options = Options()
    # Desactivar notificaciones de navegador que pueden bloquear elementos
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)
    
    session = InstagramSession(driver)
    driver.get("https://www.instagram.com")
    
    if not session.load_cookies():
        session.save_cookies()

    resultados = []

    for index, row in df_ig.iterrows():
        url = row['URL']
        print(f"Analizando: {url}")
        
        try:
            driver.get(url)
            
            # 1. Espera flexible: Esperamos a que aparezca CUALQUIER texto 
            # o que el cuerpo de la página esté listo (máximo 12 segundos)
            WebDriverWait(driver, 12).until(
                lambda d: d.find_element(By.TAG_NAME, "body").text != ""
            )
            
            # Pequeña pausa extra para que el JS renderice el contenido del post
            time.sleep(3)
            
            # 2. Captura de texto multicanal
            # Intentamos sacar el texto del 'main' que es donde está el contenido real
            try:
                contenedor_principal = driver.find_element(By.TAG_NAME, "main")
                texto_pagina = contenedor_principal.text
            except:
                # Si falla el 'main', vamos al body completo
                texto_pagina = driver.find_element(By.TAG_NAME, "body").text
            
            # 3. Verificación mejorada (Case Insensitive)
            if "bridgerton" in texto_pagina.lower():
                resultados.append("Contiene 'Bridgerton'")
            else:
                resultados.append("No menciona la serie")
                
        except Exception as e:
            # Capturamos el error real para depurar
            error_msg = str(e).split('\n')[0] # Solo la primera línea del error
            resultados.append(f"Error: {error_msg}")
            print(f"Fallo en {url}: {error_msg}")
        
        time.sleep(1) # Respiro entre links

    df_ig['Verificacion'] = resultados
    df_ig.to_excel('resultados_instagram_final.xlsx', index=False)
    print("\n🚀 Proceso finalizado con éxito.")
    driver.quit()

# --- 3. EJECUCIÓN ---
if __name__ == "__main__":
    verificar_instagram_bridgerton()