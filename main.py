import os
import time
import json
import logging
from datetime import datetime
from threading import Thread
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = "TU_TOKEN_AQUI"
OWNER_ID = 882455317

GROUPS_FILE = "groups.json"
TEXT_FILE = "text.txt"
IMAGE_FILE = "image.jpg"
COOKIES_FILE = "cookies.txt"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

auto_mode = {"active": False}
scheduler = BackgroundScheduler()
scheduler.start()

def save_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def load_file(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def send_startup_message():
    bot.send_message(chat_id=OWNER_ID, text="Bot iniciado correctamente y en funcionamiento.")

def start(update: Update, context: CallbackContext):
    if update.effective_user.id == OWNER_ID:
        update.message.reply_text("Hola, el bot está activo. Usa /help para ver comandos.")

def help_command(update: Update, context: CallbackContext):
    if update.effective_user.id == OWNER_ID:
        update.message.reply_text("/start - Ver estado del bot
/set_text - Guardar texto
/set_image - Guardar imagen
/set_groups - Guardar enlaces de grupos
/view_config - Ver configuración actual
/set_cookies - Cambiar cookies de Facebook
/auto_on - Activar publicaciones automáticas
/auto_off - Desactivar publicaciones automáticas")

def set_text(update: Update, context: CallbackContext):
    if update.effective_user.id == OWNER_ID:
        text = update.message.text.replace('/set_text ', '')
        save_file(TEXT_FILE, text)
        update.message.reply_text("Texto guardado.")

def set_image(update: Update, context: CallbackContext):
    if update.effective_user.id == OWNER_ID and update.message.photo:
        photo_file = update.message.photo[-1].get_file()
        photo_file.download(IMAGE_FILE)
        update.message.reply_text("Imagen guardada.")

def set_groups(update: Update, context: CallbackContext):
    if update.effective_user.id == OWNER_ID:
        groups = update.message.text.replace('/set_groups ', '').split()
        save_file(GROUPS_FILE, json.dumps(groups))
        update.message.reply_text("Grupos guardados.")

def set_cookies(update: Update, context: CallbackContext):
    if update.effective_user.id == OWNER_ID:
        cookies = update.message.text.replace('/set_cookies ', '')
        save_file(COOKIES_FILE, cookies)
        update.message.reply_text("Cookies guardadas.")

def view_config(update: Update, context: CallbackContext):
    if update.effective_user.id == OWNER_ID:
        text = load_file(TEXT_FILE) or "No hay texto."
        groups = json.loads(load_file(GROUPS_FILE) or "[]")
        cookies = load_file(COOKIES_FILE) or "No hay cookies."
        msg = f"Texto: {text}\nImagen: {'Sí' if os.path.exists(IMAGE_FILE) else 'No'}\nCookies: {'Sí' if cookies else 'No'}\nGrupos: "
        for i, g in enumerate(groups, 1):
            msg += f"\n{i}. {g}"
        update.message.reply_text(msg)

def publish_to_facebook():
    text = load_file(TEXT_FILE)
    cookies = load_file(COOKIES_FILE)
    groups = json.loads(load_file(GROUPS_FILE) or "[]")
    for i, group in enumerate(groups):
        # Aquí iría la lógica real de publicación con cookies
        print(f"Publicando en {group}: {text}")
        time.sleep(10)

def auto_publish():
    if auto_mode["active"]:
        publish_to_facebook()

def auto_on(update: Update, context: CallbackContext):
    if update.effective_user.id == OWNER_ID:
        auto_mode["active"] = True
        scheduler.add_job(auto_publish, 'cron', hour=8, minute=0, id='morning')
        scheduler.add_job(auto_publish, 'cron', hour=18, minute=0, id='evening')
        update.message.reply_text("Modo automático activado.")

def auto_off(update: Update, context: CallbackContext):
    if update.effective_user.id == OWNER_ID:
        auto_mode["active"] = False
        scheduler.remove_all_jobs()
        update.message.reply_text("Modo automático desactivado.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("set_text", set_text))
dispatcher.add_handler(CommandHandler("set_groups", set_groups))
dispatcher.add_handler(CommandHandler("set_cookies", set_cookies))
dispatcher.add_handler(CommandHandler("view_config", view_config))
dispatcher.add_handler(CommandHandler("auto_on", auto_on))
dispatcher.add_handler(CommandHandler("auto_off", auto_off))
dispatcher.add_handler(MessageHandler(Filters.photo, set_image))

Thread(target=send_startup_message).start()
updater.start_polling()
updater.idle()