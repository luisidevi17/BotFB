from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import logging

def publicar_en_facebook(cookies, grupo_url, mensaje, ruta_imagen=None):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.facebook.com/")
        driver.delete_all_cookies()

        # Agregar cookies al navegador
        for parte in cookies.split(";"):
            if "=" in parte:
                nombre, valor = parte.strip().split("=", 1)
                driver.add_cookie({"name": nombre, "value": valor, "domain": ".facebook.com"})

        driver.get(grupo_url)
        time.sleep(5)

        logging.info("🌀 Página del grupo cargada. Buscando caja de publicación...")

        # Buscar la caja de publicación
        caja = driver.find_element(By.XPATH, "//div[contains(text(), 'Escribe algo') or contains(text(), 'Write something')]")
        caja.click()
        time.sleep(2)

        # Escribir el mensaje
        area = driver.find_element(By.XPATH, "//div[@role='textbox']")
        area.send_keys(mensaje)
        time.sleep(2)

        # Subir imagen si hay
        if ruta_imagen:
            subir = driver.find_element(By.XPATH, "//input[@type='file']")
            subir.send_keys(ruta_imagen)
            time.sleep(5)

        # Buscar y dar clic al botón de publicar
        botones = driver.find_elements(By.XPATH, "//div[@aria-label='Publicar' or @aria-label='Post']")
        for b in botones:
            if b.is_displayed():
                b.click()
                logging.info("✅ Publicación enviada.")
                break

        time.sleep(5)

    except Exception as e:
        logging.error(f"❌ Error publicando: {e}")
    finally:
        driver.quit()
