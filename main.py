import time
import random
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Carga configuración
def load_config():
    with open('config.yaml') as f:
        return yaml.safe_load(f)

# Inicia navegador en modo headless def start_browser(cookies):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://m.facebook.com')

    # Carga cookies para mantener sesión
    for name, val in cookies.items():
        driver.add_cookie({'name': name, 'value': val, 'domain': '.facebook.com'})
    driver.refresh()
    return driver

# Publica en un grupo def post_to_group(driver, group_url, message, image_path):
    driver.get(group_url + '/create_post')
    time.sleep(3)
    # Texto
elem = driver.find_element_by_tag_name('textarea')
elem.send_keys(message)
    # Imagen
ear = driver.find_element_by_xpath("//input[@type='file']")
    ear.send_keys(image_path)
    time.sleep(2)
    # Botón publicar
driver.find_element_by_xpath("//button[contains(., 'Publicar')]").click()
    time.sleep(random.randint(90, 180))

# Flujo principal
def run_poster():
    cfg = load_config()
    cookies = {'c_user': cfg['facebook']['c_user'], 'xs': cfg['facebook']['xs']}
    driver = start_browser(cookies)

    message = cfg['content']['text']
    image = cfg['content']['image']
    groups = cfg['facebook']['groups']

    for idx, grp in enumerate(groups, 1):
        try:
            post_to_group(driver, grp, message, image)
            print(f"[{idx}/{len(groups)}] Publicado en {grp}")
        except Exception as e:
            print(f"Error en {grp}: {e}")
    driver.quit()

if __name__ == '__main__':
    run_poster()