import requests
from bs4 import BeautifulSoup
import logging
import time

logger = logging.getLogger(__name__)

def publicar_en_facebook(cookies, grupo_url, mensaje, ruta_imagen=None):
    session = requests.Session()
    # Parsear cookies
    for c in cookies.split(";"):
        if "=" in c:
            k, v = c.strip().split("=", 1)
            session.cookies[k] = v

    headers = {"User-Agent": "Mozilla/5.0"}
    url = grupo_url.replace("www.", "mbasic.")
    resp = session.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    dtsg = soup.find("input", {"name": "fb_dtsg"})["value"]
    jazoest = soup.find("input", {"name": "jazoest"})["value"]
    action = soup.find("form", {"method": "post"})["action"]
    post_url = "https://mbasic.facebook.com" + action

    data = {"fb_dtsg": dtsg, "jazoest": jazoest, "xc_message": mensaje}
    files = {}
    if ruta_imagen:
        files["pic"] = open(ruta_imagen, "rb")

    resultado = session.post(post_url, headers=headers, data=data, files=files)
    time.sleep(2)
    if resultado.ok:
        logger.info(f"Publicado en {grupo_url}")
        return True
    else:
        logger.error(f"Error {resultado.status_code}: {resultado.text}")
        return False
