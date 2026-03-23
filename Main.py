import asyncio
from Scraper import GoogleScraper
from verificador import IAVerificador
from perfiles_ig import ProfileCleaner
from utils import cargar_urls_procesadas, guardar_urls_procesadas
import os
import pandas as pd

class Main:

    @staticmethod
    def run():

        tema = "Baja California noticias"

        print("\n📰 INICIANDO PIPELINE\n")

        # =====================================================
        # 1️⃣ GOOGLE SCRAPER
        # =====================================================
        google_scraper = GoogleScraper(tema)
        df_links = google_scraper.ejecutar()

        print("🔎 URLs encontradas:", len(df_links))

        # =====================================================
        # 2️⃣ FILTRAR URLs YA PROCESADAS
        # =====================================================
        urls_procesadas = cargar_urls_procesadas()
        df_links = df_links[~df_links["URL"].isin(urls_procesadas)]

        print("🆕 URLs nuevas:", len(df_links))

        if df_links.empty:
            print("✅ No hay URLs nuevas")
            return

        # =====================================================
        # 3️⃣ IA → FILTRAR POR BAJA CALIFORNIA
        # =====================================================
        ia = IAVerificador()
        df_verificado = ia.ejecutar(df_links, tema)

        df_verificado = df_verificado[
            df_verificado["Resultado_Verificacion"] == "RELACIONADO_BAJA_CALIFORNIA"
        ]

        print("📍 Contenido de Baja California:", len(df_verificado))

        if df_verificado.empty:
            print("❌ No hay contenido relevante")
            return

        # =====================================================
        # 4️⃣ LIMPIAR PERFILES (REDES)
        # =====================================================
        cleaner = ProfileCleaner()
        df_limpio = asyncio.run(cleaner.ejecutar(df_verificado))

        print("🧹 Perfiles detectados:", len(df_limpio))

        if df_limpio.empty:
            print("❌ No hay datos limpios")
            return

        # =====================================================
        # 5️⃣ GUARDAR SIN DUPLICADOS (EXCEL)
        # =====================================================
        archivo = "medios_baja_california.xlsx"

        if os.path.exists(archivo):
            df_existente = pd.read_excel(archivo)

            df_total = pd.concat([df_existente, df_limpio])
            df_total = df_total.drop_duplicates(subset=["URL_Limpia"])

        else:
            df_total = df_limpio

        df_total.to_excel(archivo, index=False)

        print("💾 Datos guardados en Excel")

        # =====================================================
        # 6️⃣ GUARDAR URLs PROCESADAS (CLAVE 🔥)
        # =====================================================
        guardar_urls_procesadas(df_limpio["URL"].tolist())

        print("🧠 URLs guardadas para evitar reprocesar")

        print("\n✅ PIPELINE FINALIZADO")


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    Main.run()