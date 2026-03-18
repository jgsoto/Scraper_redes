import asyncio
from Scraper import GoogleScraper
from verificador import IAVerificador
from perfiles_ig import ProfileCleaner

class Main:

    @staticmethod
    def run():

        serie = "Sandokan"

        print("\n🎬 INICIANDO PIPELINE COMPLETO\n")

        # =====================================================
        # 1️⃣ GOOGLE SCRAPER
        # =====================================================
        google_scraper = GoogleScraper(serie)
        df_links = google_scraper.ejecutar()

        print("🔎 URLs encontradas:", len(df_links))

        if df_links.empty:
            print("❌ No se encontraron URLs")
            return

        # =====================================================
        # 2️⃣ VERIFICACIÓN CON IA
        # =====================================================
        ia = IAVerificador()
        df_verificado = ia.ejecutar(df_links, serie)

        df_verificado = df_verificado[
            df_verificado["Resultado_Verificacion"] == "RELACIONADO"
        ]

        print("🤖 URLs relacionadas:", len(df_verificado))

        if df_verificado.empty:
            print("❌ Ninguna URL relevante")
            return

        # =====================================================
        # 3️⃣ LIMPIEZA DE PERFILES
        # =====================================================
        cleaner = ProfileCleaner()
        df_limpio = asyncio.run(
            cleaner.ejecutar(df_verificado)
        )

        print("🧹 Perfiles limpios:", len(df_limpio))

        # =====================================================
        # 4️⃣ GUARDAR RESULTADO FINAL
        # =====================================================
        df_limpio.to_excel("resultado_final.xlsx", index=False)

        print("\n✅ PIPELINE COMPLETO FINALIZADO")

# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    Main.run()