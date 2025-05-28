import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def publicar_en_facebook(cookies, grupo_url, mensaje, ruta_imagen=None):
    logging.info("🟡 Iniciando publicación...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.facebook.com/")
        driver.delete_all_cookies()
        logging.info("✅ Página de Facebook cargada")

        for parte in cookies.split(";"):
            if "=" in parte:
                nombre, valor = parte.strip().split("=", 1)
                driver.add_cookie({
                    "name": nombre.strip(),
                    "value": valor.strip(),
                    "domain": ".facebook.com"
                })
        logging.info("✅ Cookies añadidas")

        driver.get(grupo_url)
        time.sleep(5)
        logging.info("✅ Grupo cargado: " + grupo_url)

        try:
            caja = driver.find_element(By.XPATH, "//div[contains(text(), 'Escribe algo') or contains(text(), 'Write something')]")
            caja.click()
            logging.info("✅ Caja de publicación encontrada y clickeada")
        except Exception as e:
            logging.error("❌ No se encontró la caja de publicación. Error: " + str(e))
            return

        time.sleep(2)

        try:
            area = driver.find_element(By.XPATH, "//div[@role='textbox']")
            area.send_keys(mensaje)
            logging.info("✅ Mensaje escrito")
        except Exception as e:
            logging.error("❌ No se pudo escribir el mensaje. Error: " + str(e))
            return

        if ruta_imagen:
            try:
                subir = driver.find_element(By.XPATH, "//input[@type='file']")
                subir.send_keys(ruta_imagen)
                logging.info("✅ Imagen cargada")
                time.sleep(5)
            except Exception as e:
                logging.error("❌ Error al subir imagen. Error: " + str(e))

        try:
            botones = driver.find_elements(By.XPATH, "//div[@aria-label='Publicar' or @aria-label='Post']")
            for b in botones:
                if b.is_displayed():
                    b.click()
                    logging.info("✅ Clic en 'Publicar' hecho")
                    break
            else:
                logging.error("❌ Botón de publicar no encontrado")
        except Exception as e:
            logging.error("❌ Error al intentar publicar. Error: " + str(e))

        time.sleep(5)

    except Exception as e:
        logging.error("❌ Error inesperado en publicar_en_facebook: " + str(e))
    finally:
        driver.quit()
        logging.info("🔚 Navegador cerrado")
