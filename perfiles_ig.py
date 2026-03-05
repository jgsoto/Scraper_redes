import asyncio
import re
import pandas as pd
from playwright.async_api import async_playwright
from urllib.parse import urlparse

def limpiar_url_generica(url):
    parsed = urlparse(url)
    dominio = parsed.netloc.lower()
    path = parsed.path.strip("/")
    partes = path.split("/")

    if not partes:
        return None

    # FACEBOOK
    if "facebook.com" in dominio:
        if partes[0] not in ["posts", "videos", "photo.php", "groups"]:
            return f"https://www.facebook.com/{partes[0]}/"

    # X / TWITTER
    if "x.com" in dominio or "twitter.com" in dominio:
        usuario = partes[0]

        # Ignorar rutas internas
        if usuario not in [
            "home",
            "explore",
            "notifications",
            "i",
            "search",
            "intent",
            "share"
        ]:
            return f"https://x.com/{usuario}"

    # TIKTOK
    if "tiktok.com" in dominio:
        if partes[0].startswith("@"):
            return f"https://www.tiktok.com/{partes[0]}"
    
    return None

async def obtener_html(page, url):
    await page.goto(url, timeout=30000)
    await page.wait_for_load_state("networkidle")
    return await page.content()

def extraer_usuario_instagram(html):
    match = re.search(r'"username":"(.*?)"', html)
    if match:
        return f"https://www.instagram.com/{match.group(1)}/"
    return None

def extraer_canal_youtube(html):
    match = re.search(r'"ownerProfileUrl":"(.*?)"', html)
    if match:
        canal = match.group(1).replace("\\/", "/")
        return f"{canal}"
    return None

async def procesar_excel(entrada, salida):
    df = pd.read_excel(entrada)
    perfiles = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for url in df["URL"]:
            print("Procesando:", url)
            perfil = None

            try:
                html = await obtener_html(page, url)
                
                                         
                if "instagram.com/p/" in url:
                    perfil = extraer_usuario_instagram(html)
                
                elif "youtube.com/watch" in url:
                    perfil = extraer_canal_youtube(html)

                else:
                    perfil = limpiar_url_generica(url)

            except Exception as e:
                print("Error:", e)

            perfiles.append(perfil)

        await browser.close()

    df["URL"] = perfiles
    df = df[df["URL"].notnull()]
    df = df.drop_duplicates(subset=["URL"])
    df.to_excel(salida, index=False)

    print("Proceso terminado ✅")


if __name__ == "__main__":
    entrada = input("Excel entrada: ")
    salida = input("Excel salida: ")

    asyncio.run(procesar_excel(entrada, salida))