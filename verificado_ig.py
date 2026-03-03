import os
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrapper_multired_pro():
    # 1. Configuración de Carpeta de Perfil (ESTO ES LA CLAVE)
    # Crea una carpeta llamada 'perfil_selenium' en tu proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    user_data_dir = os.path.join(script_dir, "perfil_selenium")
    
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    options = Options()
    options.add_argument(f"--user-data-dir={user_data_dir}") # Guarda cookies, caché y sesiones
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        df = pd.read_excel('paginas_encontradas_Agata.xlsx')
        # Limpiar links: quedarnos solo con redes sociales soportadas
        redes_validas = ["instagram.com", "facebook.com", "x.com", "youtube.com", "tiktok.com"]
        df_filtrado = df[df['URL'].str.contains('|'.join(redes_validas), na=False)].copy()
    except Exception as e:
        print(f"Error con el Excel: {e}")
        return

    resultados = []

    # 2. PRIMER PASO: Verificación de Login General
    # Solo lo haremos una vez al principio del script
    print("\n[!] Revisando sesiones activas...")
    for red in ["https://www.instagram.com", "https://www.facebook.com"]:
        driver.get(red)
        time.sleep(3)
        # Si ves que te pide login, el script se detendrá aquí para que lo hagas
        if "login" in driver.current_url.lower() or "signup" in driver.current_url.lower():
            print(f"⚠️ No hay sesión en {red}. Por favor, loguéate manualmente.")
            input("Cuando estés dentro de la cuenta y veas el muro, presiona ENTER aquí...")

    # 3. PROCESAMIENTO DE LINKS
    for index, row in df_filtrado.iterrows():
        url = row['URL']
        print(f"🚀 Analizando: {url}")
        
        try:
            driver.get(url)
            
            # Espera a que el contenido principal cargue
            # En Instagram los posts están dentro de etiquetas <article> o <main>
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(4) # Tiempo para que el texto dinámico aparezca

            # Extraer el texto
            texto_completo = driver.find_element(By.TAG_NAME, "body").text
            
            if "Agatha Christie: Las Siete Esferas" in texto_completo.lower():
                resultados.append("SÍ: Contiene Agata")
            else:
                resultados.append("NO: No encontrado")

        except Exception as e:
            resultados.append(f"Error de carga: {type(e).__name__}")
            print(f"❌ Falló {url}")

    # 4. GUARDADO FINAL (Sobrescribiendo)
    df_filtrado['Verificacion'] = resultados
    df_filtrado.to_excel('verificacion_final_Agata.xlsx', index=False)
    print("\n✅ Proceso completado. Archivo 'verificacion_final.xlsx' generado.")
    driver.quit()

if __name__ == "__main__":
    scrapper_multired_pro()