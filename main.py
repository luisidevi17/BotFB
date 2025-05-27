import os
import json
import logging
import threading
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from apscheduler.schedulers.background import BackgroundScheduler

# Configuración de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes y variables globales
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "882455317"))  # Tu ID de Telegram
DATA_FILE = "data.json"

# Inicializar bot y datos
bot = Bot(token=TELEGRAM_TOKEN)
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Leer datos
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"groups": [], "text": "", "image": "", "auto": False, "account": "default"}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Guardar datos
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Comandos
def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot activo y funcionando.")
    context.bot.send_message(chat_id=ADMIN_ID, text="Bot desplegado y funcionando correctamente.")

def help_command(update: Update, context: CallbackContext):
    comandos = [
        "/start - Verificar que el bot está activo",
        "/help - Mostrar este mensaje de ayuda",
        "/ver - Ver configuración actual del bot",
        "/activar - Activar publicaciones automáticas",
        "/desactivar - Desactivar publicaciones automáticas",
        "/cambiarcuenta - Cambiar cuenta de Facebook (en desarrollo)"
    ]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Comandos disponibles:
" + "
".join(comandos))

def ver(update: Update, context: CallbackContext):
    data = load_data()
    grupos = "
".join([f"{i+1}. {g}" for i, g in enumerate(data['groups'])])
    mensaje = f"Texto actual: {data['text']}
Imagen: {data['image']}
Grupos:
{grupos}
Modo automático: {'Activado' if data['auto'] else 'Desactivado'}
Cuenta: {data['account']}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje)

def activar(update: Update, context: CallbackContext):
    data = load_data()
    data["auto"] = True
    save_data(data)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Modo automático activado.")

def desactivar(update: Update, context: CallbackContext):
    data = load_data()
    data["auto"] = False
    save_data(data)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Modo automático desactivado.")

# Manejar mensajes con contenido
def handle_message(update: Update, context: CallbackContext):
    data = load_data()
    if update.message.text:
        data["text"] = update.message.text
    if update.message.photo:
        file = update.message.photo[-1].get_file()
        path = "imagen.jpg"
        file.download(path)
        data["image"] = path
    save_data(data)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Contenido guardado.")

# Publicación simulada (ajusta con lógica real de Facebook)
def publicar():
    data = load_data()
    if data["auto"]:
        for i, grupo in enumerate(data["groups"]):
            logger.info(f"Publicando en grupo {i+1}: {grupo} con texto: {data['text']}")

# Agendar publicaciones
scheduler = BackgroundScheduler()
scheduler.add_job(publicar, "cron", hour=8)
scheduler.add_job(publicar, "cron", hour=18)
scheduler.start()

# Asignar comandos
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("ver", ver))
dispatcher.add_handler(CommandHandler("activar", activar))
dispatcher.add_handler(CommandHandler("desactivar", desactivar))
dispatcher.add_handler(MessageHandler(Filters.text | Filters.photo, handle_message))

# Iniciar bot
updater.start_polling()
updater.idle()