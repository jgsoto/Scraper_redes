from urllib.parse import urlparse
import re
from playwright.async_api import async_playwright

class ProfileCleaner:

    def limpiar_url_generica(self, url):
        if not url or not isinstance(url, str):
            return None
            
        parsed = urlparse(url)
        dominio = parsed.netloc.lower()
        path = parsed.path.strip("/")
        partes = path.split("/")

        if not partes or partes[0] == "":
            return None

        if "facebook.com" in dominio:
            if partes[0] not in ["posts", "videos", "photo.php", "groups"]:
                return f"https://www.facebook.com/{partes[0]}/"

        if "x.com" in dominio or "twitter.com" in dominio:
            usuario = partes[0]
            if usuario not in ["home", "explore", "notifications", "i", "search", "intent", "share"]:
                return f"https://x.com/{usuario}"

        if "tiktok.com" in dominio:
            if partes[0].startswith("@"):
                return f"https://www.tiktok.com/{partes[0]}"

        return None

    # -------------------------
    # INSTAGRAM MEJORADO
    # -------------------------
    async def obtener_perfil_instagram(self, page):
        try:
            await page.wait_for_timeout(3000)
            
            # Intento 1: Buscar el enlace al perfil en la interfaz (más seguro)
            enlace_perfil = await page.query_selector("header a[href^='/']")
            if enlace_perfil:
                href = await enlace_perfil.get_attribute("href")
                usuario = href.replace("/", "").split("?")[0]
                return f"https://www.instagram.com/{usuario}/"

            # Intento 2: Limpieza profunda del og:title
            meta = await page.query_selector("meta[property='og:title']")
            if meta:
                content = await meta.get_attribute("content")
                # El formato suele ser "Nombre (@usuario) • Fotos y videos..."
                if "@" in content:
                    usuario = content.split("@")[-1].split(")")[0]
                    # Limpiar por si queda basura
                    usuario = usuario.strip().split(" ")[0]
                    return f"https://www.instagram.com/{usuario}/"
            
            return None
        except:
            return None

    # -------------------------
    # YOUTUBE MEJORADO
    # -------------------------
    async def obtener_canal_youtube(self, page):
        try:
            await page.wait_for_timeout(3000)
            
            # Buscar el link del canal en los metadatos de YouTube
            meta_url = await page.query_selector("link[itemprop='url']")
            if meta_url:
                href = await meta_url.get_attribute("href")
                if href:
                    if href.startswith("/"):
                        return f"https://www.youtube.com{href}"
                    return href

            # Alternativa: Buscar el link del autor debajo del video
            canal_link = await page.query_selector("#upload-info a[href*='/@'], #upload-info a[href*='/channel/']")
            if canal_link:
                href = await canal_link.get_attribute("href")
                if href.startswith("/"):
                    return f"https://www.youtube.com{href}"
                return href

        except:
            return None
        return None

    # -------------------------
    # EJECUCIÓN
    # -------------------------
    async def ejecutar(self, df):
        df = df.copy()
        perfiles = []

        async with async_playwright() as p:
            # Usar un User-Agent normal para evitar bloqueos y obtener metas correctos
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            for url in df["URL"]:
                # 1. Intentar limpiar si ya es una URL de perfil
                perfil = self.limpiar_url_generica(url)

                # 2. Si es un post/video, navegar para encontrar al autor
                if perfil is None:
                    try:
                        await page.goto(url, timeout=45000, wait_until="domcontentloaded")

                        if "instagram.com" in url:
                            perfil = await self.obtener_perfil_instagram(page)
                        elif "youtube.com/watch" in url:
                            perfil = await self.obtener_canal_youtube(page)
                    except Exception as e:
                        print(f"Error procesando {url}: {e}")
                        perfil = None

                perfiles.append(perfil)

            await browser.close()

        df["URL_Limpia"] = perfiles
        # Limpiar filas donde no se encontró nada y quitar duplicados
        #df = df.dropna(subset=["URL_Limpia"])
        df = df.drop_duplicates(subset=["URL_Limpia"])

        return df