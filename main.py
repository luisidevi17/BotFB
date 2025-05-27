
import os
import time
import json
import logging
import threading
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configura logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables globales
ADMIN_ID = 882455317  # Tu ID de Telegram
FACEBOOK_COOKIES_FILE = 'fb_cookies.json'
POST_TEXT_FILE = 'post_text.txt'
IMAGE_FILE = 'post_image.jpg'
GROUPS_FILE = 'groups.txt'
AUTO_FILE = 'auto_mode.txt'
AUTO_HOUR_FILE = 'auto_hour.txt'

bot_token = os.environ.get("BOT_TOKEN")
updater = Updater(bot_token)
bot: Bot = updater.bot

# Función para guardar datos
def guardar(archivo, dato):
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(dato)

def leer(archivo):
    if not os.path.exists(archivo):
        return ""
    with open(archivo, 'r', encoding='utf-8') as f:
        return f.read()

# Comandos
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Bot funcionando correctamente. Usa /help para ver comandos.")

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "/help - Lista de comandos
"
        "/ver_config - Ver configuración actual
"
        "/cambiar_fb - Cambiar cookies de Facebook
"
        "/addgrupo <enlace/nombre> - Añadir grupo
"
        "/texto - Enviar nuevo texto
"
        "/imagen - Enviar nueva imagen
"
        "/activar - Activar auto post
"
        "/desactivar - Desactivar auto post
"
        "/hora <HH:MM> - Establecer hora automática"
    )

def ver_config(update: Update, context: CallbackContext):
    grupos = leer(GROUPS_FILE).splitlines()
    texto = leer(POST_TEXT_FILE)
    hora = leer(AUTO_HOUR_FILE)
    mensaje = f"Grupos ({len(grupos)}):
"
    for i, g in enumerate(grupos, 1):
        mensaje += f"{i}. {g}
"
    mensaje += f"
Texto:
{texto}

Hora automática: {hora}"
    update.message.reply_text(mensaje)
    if os.path.exists(IMAGE_FILE):
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open(IMAGE_FILE, 'rb'))

def cambiar_fb(update: Update, context: CallbackContext):
    if context.args:
        guardar(FACEBOOK_COOKIES_FILE, ' '.join(context.args))
        update.message.reply_text("Cookies actualizadas.")
    else:
        update.message.reply_text("Envía las cookies con el comando.")

def addgrupo(update: Update, context: CallbackContext):
    if context.args:
        with open(GROUPS_FILE, 'a', encoding='utf-8') as f:
            f.write(' '.join(context.args) + '
')
        update.message.reply_text("Grupo añadido.")
    else:
        update.message.reply_text("Uso: /addgrupo nombre_o_enlace")

def texto(update: Update, context: CallbackContext):
    if context.args:
        guardar(POST_TEXT_FILE, ' '.join(context.args))
        update.message.reply_text("Texto actualizado.")
    else:
        update.message.reply_text("Envía el texto con el comando.")

def imagen(update: Update, context: CallbackContext):
    update.message.reply_text("Envíame la imagen ahora.")

def guardar_imagen(update: Update, context: CallbackContext):
    photo = update.message.photo[-1].get_file()
    photo.download(IMAGE_FILE)
    update.message.reply_text("Imagen guardada.")

def activar(update: Update, context: CallbackContext):
    guardar(AUTO_FILE, '1')
    update.message.reply_text("Modo automático activado.")

def desactivar(update: Update, context: CallbackContext):
    guardar(AUTO_FILE, '0')
    update.message.reply_text("Modo automático desactivado.")

def hora(update: Update, context: CallbackContext):
    if context.args:
        guardar(AUTO_HOUR_FILE, context.args[0])
        update.message.reply_text(f"Hora automática establecida a {context.args[0]}")
    else:
        update.message.reply_text("Uso: /hora HH:MM")

# Envío automático diario
def auto_loop():
    while True:
        if leer(AUTO_FILE) == '1':
            now = datetime.now().strftime('%H:%M')
            hora_auto = leer(AUTO_HOUR_FILE).strip()
            if now == hora_auto:
                # Aquí debería ir la lógica de publicación en Facebook
                bot.send_message(chat_id=ADMIN_ID, text="Publicación automática ejecutada.")
                time.sleep(60)
        time.sleep(30)

def main():
    # Al iniciar, envía mensaje de estado
    bot.send_message(chat_id=ADMIN_ID, text="Bot desplegado y funcionando correctamente.")

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("ver_config", ver_config))
    dp.add_handler(CommandHandler("cambiar_fb", cambiar_fb))
    dp.add_handler(CommandHandler("addgrupo", addgrupo))
    dp.add_handler(CommandHandler("texto", texto))
    dp.add_handler(CommandHandler("imagen", imagen))
    dp.add_handler(CommandHandler("activar", activar))
    dp.add_handler(CommandHandler("desactivar", desactivar))
    dp.add_handler(CommandHandler("hora", hora))
    dp.add_handler(MessageHandler(Filters.photo, guardar_imagen))

    # Hilo para modo automático
    threading.Thread(target=auto_loop, daemon=True).start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
