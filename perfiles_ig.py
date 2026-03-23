from urllib.parse import urlparse
from playwright.async_api import async_playwright


class ProfileCleaner:

    # =========================================================
    # LIMPIEZA BÁSICA DE URLS
    # =========================================================
    def limpiar_url_generica(self, url):
        if not url or not isinstance(url, str):
            return None

        parsed = urlparse(url)
        dominio = parsed.netloc.lower()
        path = parsed.path.strip("/")
        partes = path.split("/")

        if not partes or partes[0] == "":
            return None

        # FACEBOOK
        if "facebook.com" in dominio:
            usuario = partes[0]
            if usuario not in ["posts", "videos", "photo.php", "groups"]:
                return f"https://www.facebook.com/{usuario}/"

        return None

    # =========================================================
    # INSTAGRAM (FIX REAL)
    # =========================================================
    async def obtener_perfil_instagram(self, page):
        try:
            await page.wait_for_timeout(5000)

            # ===============================
            # 🔥 MÉTODO 1: twitter:title (EL MEJOR)
            # ===============================
            meta = await page.query_selector("meta[name='twitter:title']")
            if meta:
                content = await meta.get_attribute("content")

                if content and "@" in content:
                    usuario = content.split("@")[-1].split(")")[0]
                    usuario = usuario.strip().split(" ")[0]

                    if usuario and usuario not in ["accounts"]:
                        return f"https://www.instagram.com/{usuario}/"

            # ===============================
            # 🔥 MÉTODO 2: og:title (backup)
            # ===============================
            meta = await page.query_selector("meta[property='og:title']")
            if meta:
                content = await meta.get_attribute("content")

                if content and "@" in content:
                    usuario = content.split("@")[-1].split(")")[0]
                    usuario = usuario.strip().split(" ")[0]

                    if usuario:
                        return f"https://www.instagram.com/{usuario}/"

            # ===============================
            # 🔥 MÉTODO 3: JSON interno (último recurso)
            # ===============================
            scripts = await page.query_selector_all("script")

            for script in scripts:
                text = await script.inner_text()

                if '"username":"' in text:
                    try:
                        usuario = text.split('"username":"')[1].split('"')[0]
                        if usuario:
                            return f"https://www.instagram.com/{usuario}/"
                    except:
                        continue

        except Exception as e:
            print("❌ IG extractor:", e)

        return None

    # =========================================================
    # YOUTUBE (FIX REAL)
    # =========================================================
    async def obtener_canal_youtube(self, page):
        try:
            await page.wait_for_timeout(4000)

            # 🔥 MÉTODO 1 (nuevo y estable)
            canal = await page.query_selector("ytd-channel-name a")
            if canal:
                href = await canal.get_attribute("href")
                if href:
                    if href.startswith("/"):
                        return f"https://www.youtube.com{href}"
                    return href

            # 🔥 MÉTODO 2 (fallback)
            meta = await page.query_selector("meta[property='og:url']")
            if meta:
                url = await meta.get_attribute("content")
                if url and ("channel" in url or "@" in url):
                    return url

        except Exception as e:
            print("❌ YT extractor:", e)

        return None

    # =========================================================
    # PIPELINE PRINCIPAL
    # =========================================================
    async def ejecutar(self, df):

        df = df.copy()
        perfiles = []

        async with async_playwright() as p:

            browser = await p.chromium.launch(headless=True)

            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )

            page = await context.new_page()

            for url in df["URL"]:

                print(f"🔗 Procesando: {url}")

                perfil = self.limpiar_url_generica(url)

                # =========================
                # INSTAGRAM
                # =========================
                if perfil is None and "instagram.com" in url:
                    try:
                        await page.goto(url, timeout=45000, wait_until="domcontentloaded")
                        perfil = await self.obtener_perfil_instagram(page)
                    except Exception as e:
                        print(f"❌ Error IG {url}: {e}")

                # =========================
                # YOUTUBE
                # =========================
                elif perfil is None and "youtube.com" in url:
                    try:
                        await page.goto(url, timeout=45000, wait_until="domcontentloaded")
                        perfil = await self.obtener_canal_youtube(page)
                    except Exception as e:
                        print(f"❌ Error YT {url}: {e}")

                # =========================
                # FALLBACK (NO PERDER DATA)
                # =========================
                if not perfil:
                    perfil = url

                print(f"   → Limpio: {perfil}")

                perfiles.append(perfil)

            await browser.close()

        # =========================================================
        # OUTPUT
        # =========================================================
        df["URL_Limpia"] = perfiles

        print("ANTES DE DEDUP:", len(df))

        # 🔥 MÁS SEGURO (no elimina todo)
        df = df.drop_duplicates(subset=["URL_Limpia"], keep="first")

        print("DESPUÉS DE DEDUP:", len(df))

        return df