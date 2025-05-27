from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def publicar_en_facebook(cookies, grupo_url, mensaje, ruta_imagen=None):
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=opts)

    try:
        driver.get("https://facebook.com")
        for cookie in cookies.split(";"):
            if "=" in cookie:
                name, value = cookie.strip().split("=", 1)
                driver.add_cookie({"name": name.strip(), "value": value.strip()})
        driver.get(grupo_url)
        time.sleep(5)

        caja = driver.find_element(By.XPATH, "//div[contains(@aria-label, 'Escribe algo') or contains(@aria-label, 'Write something')]")
        caja.click()
        time.sleep(2)

        editable = driver.find_element(By.XPATH, "//div[@role='textbox']")
        editable.send_keys(mensaje)
        time.sleep(2)

        if ruta_imagen:
            subir = driver.find_element(By.XPATH, "//input[@type='file']")
            subir.send_keys(ruta_imagen)
            time.sleep(5)

        boton_publicar = driver.find_element(By.XPATH, "//div[@aria-label='Publicar' or @aria-label='Post']")
        boton_publicar.click()
        time.sleep(5)
    except Exception as e:
        print("Error al publicar:", e)
    finally:
        driver.quit()