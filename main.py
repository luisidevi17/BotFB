import os
import time
import json
import logging
import threading
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

Configura logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) logger = logging.getLogger(name)

Variables globales

stored_text = "" stored_image_path = "" group_list = [] auto_mode = False scheduled_times = [] last_post_minute = None

Verifica variables de entorno necesarias

try: TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID")) FB_COOKIES = json.loads(os.getenv("FACEBOOK_COOKIES")) except Exception as e: raise ValueError("Faltan o son inválidas las variables de entorno necesarias: TELEGRAM_TOKEN, TELEGRAM_USER_ID, FACEBOOK_COOKIES")

Función para restringir comandos solo a tu usuario

def restricted(func): def wrapped(update: Update, context: CallbackContext, *args, **kwargs): if update.effective_user.id != TELEGRAM_USER_ID: update.message.reply_text("No tienes permiso para usar este bot.") return return func(update, context, *args, **kwargs) return wrapped

Publicar en grupo de Facebook (simulado)

def publish_to_facebook(group_url, text, image_path): headers = { 'Cookie': '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in FB_COOKIES]), 'User-Agent': 'Mozilla/5.0', } logger.info(f"Publicando en {group_url} con texto: {text} y imagen: {image_path}") # Aquí se haría la petición real a Facebook si se implementa.

@restricted def set_text(update: Update, context: CallbackContext): global stored_text stored_text = update.message.text.replace('/set_text ', '') update.message.reply_text("Texto guardado.")

@restricted def set_image(update: Update, context: CallbackContext): global stored_image_path file = update.message.photo[-1].get_file() file_path = f"image_{int(time.time())}.jpg" file.download(file_path) stored_image_path = file_path update.message.reply_text("Imagen guardada.")

@restricted def add_group(update: Update, context: CallbackContext): global group_list url = update.message.text.replace('/add_group ', '').strip() if url not in group_list: group_list.append(url) update.message.reply_text("Grupo añadido.") else: update.message.reply_text("Ya estaba en la lista.")

@restricted def remove_group(update: Update, context: CallbackContext): global group_list url = update.message.text.replace('/remove_group ', '').strip() if url in group_list: group_list.remove(url) update.message.reply_text("Grupo eliminado.") else: update.message.reply_text("No estaba en la lista.")

@restricted def list_groups(update: Update, context: CallbackContext): if not group_list: update.message.reply_text("No hay grupos.") else: update.message.reply_text("Grupos configurados:\n" + '\n'.join(group_list))

@restricted def public_now(update: Update, context: CallbackContext): if not stored_text and not stored_image_path: update.message.reply_text("No hay contenido almacenado para publicar.") return

success = 0
failed = 0

for group_url in group_list:
    try:
        publish_to_facebook(group_url, stored_text, stored_image_path)
        success += 1
        time.sleep(15)
    except Exception as e:
        failed += 1
        logger.error(f"Error publicando en {group_url}: {e}")

update.message.reply_text(f"✅ Publicación completada.\nÉxitos: {success}\nFallos: {failed}")

@restricted def set_hour(update: Update, context: CallbackContext): global scheduled_times try: times = update.message.text.replace('/set_hour ', '').strip().split(',') scheduled_times = [datetime.strptime(t.strip(), "%H:%M").strftime("%H:%M") for t in times] update.message.reply_text(f"Horas programadas: {', '.join(scheduled_times)}") except ValueError: update.message.reply_text("Formato inválido. Usa HH:MM, por ejemplo: 08:00,18:00")

@restricted def toggle_auto(update: Update, context: CallbackContext): global auto_mode auto_mode = not auto_mode status = "activado" if auto_mode else "desactivado" update.message.reply_text(f"Modo automático {status}.")

def auto_post_job(): global last_post_minute while True: now = datetime.now() current_time = now.strftime("%H:%M") if auto_mode and current_time in scheduled_times: if last_post_minute != current_time: logger.info("Publicación automática activada.") for group_url in group_list: try: publish_to_facebook(group_url, stored_text, stored_image_path) time.sleep(15) except Exception as e: logger.error(f"Error en publicación automática: {e}") last_post_minute = current_time time.sleep(30)

def main(): updater = Updater(TELEGRAM_TOKEN, use_context=True) dp = updater.dispatcher

dp.add_handler(CommandHandler("set_text", set_text))
dp.add_handler(MessageHandler(Filters.photo, set_image))
dp.add_handler(CommandHandler("add_group", add_group))
dp.add_handler(CommandHandler("remove_group", remove_group))
dp.add_handler(CommandHandler("list_groups", list_groups))
dp.add_handler(CommandHandler("public_now", public_now))
dp.add_handler(CommandHandler("set_hour", set_hour))
dp.add_handler(CommandHandler("toggle_auto", toggle_auto))

threading.Thread(target=auto_post_job, daemon=True).start()

updater.start_polling()
updater.idle()

if name == "main": main()

