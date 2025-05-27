import os
import time
import json
import logging
from datetime import datetime
from threading import Thread
from telegram import Update, Bot, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from keep_alive import keep_alive  # Importa keep_alive

keep_alive()  # Mantiene activo el bot en Replit

# Configura logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "TU_TOKEN_DE_TELEGRAM"
OWNER_ID = 882455317  # Tu ID de Telegram

DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {
            "texto": "",
            "imagen": None,
            "cookies": "",
            "grupos": [],
            "modo_auto": False,
            "horarios": ["08:00", "18:00"]
        }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

data = load_data()

# Función de publicación (simulada, reemplazar con requests a Facebook)
def publicar():
    texto = data['texto']
    imagen = data['imagen']
    grupos = data['grupos']
    cookies = data['cookies']

    if not texto or not cookies or not grupos:
        print("Faltan datos para publicar.")
        return

    for i, grupo in enumerate(grupos, 1):
        print(f"{i} - Publicando en {grupo}...")
        time.sleep(3)  # Simula tiempo de espera entre publicaciones
    print("¡Publicación completada!")

def auto_publicar():
    if data["modo_auto"]:
        publicar()

def start(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    update.message.reply_text("¡Bot activo y funcionando!")

def help_command(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    update.message.reply_text("""Comandos disponibles:
/start - Confirmar que el bot está activo
/help - Ver los comandos
/texto <mensaje> - Guardar texto de publicación
/imagen - Enviar imagen para publicar
/cookies <cadena> - Establecer cookies de Facebook
/grupos - Ver grupos
/agregargrupo <nombre> - Agregar grupo
/borrargrupos - Eliminar todos los grupos
/activar - Activar modo automático
/desactivar - Desactivar modo automático
/ver - Ver configuración actual
""")

def ver(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    grupos = "\n".join([f"{i+1}- {g}" for i, g in enumerate(data["grupos"])])
    resumen = f"""Texto: {data['texto'] or 'Ninguno'}
Imagen: {'Sí' if data['imagen'] else 'No'}
Cookies: {'Sí' if data['cookies'] else 'No'}
Modo automático: {'Activo' if data['modo_auto'] else 'Inactivo'}
Grupos:
{grupos or 'Ninguno'}"""
    update.message.reply_text(resumen)

def texto(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    msg = " ".join(context.args)
    data['texto'] = msg
    save_data(data)
    update.message.reply_text("Texto guardado.")

def imagen(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    if update.message.photo:
        file = update.message.photo[-1].get_file()
        file.download('imagen.jpg')
        data['imagen'] = 'imagen.jpg'
        save_data(data)
        update.message.reply_text("Imagen guardada.")
    else:
        update.message.reply_text("Envía una imagen junto con el comando.")

def cookies(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    cks = " ".join(context.args)
    data['cookies'] = cks
    save_data(data)
    update.message.reply_text("Cookies guardadas.")

def agregar_grupo(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    grupo = " ".join(context.args)
    if grupo:
        data["grupos"].append(grupo)
        save_data(data)
        update.message.reply_text("Grupo agregado.")
    else:
        update.message.reply_text("Envía un nombre o enlace del grupo.")

def borrar_grupos(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    data["grupos"] = []
    save_data(data)
    update.message.reply_text("Todos los grupos eliminados.")

def activar(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    data["modo_auto"] = True
    save_data(data)
    update.message.reply_text("Modo automático activado.")

def desactivar(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    data["modo_auto"] = False
    save_data(data)
    update.message.reply_text("Modo automático desactivado.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("ver", ver))
    dp.add_handler(CommandHandler("texto", texto))
    dp.add_handler(CommandHandler("imagen", imagen))
    dp.add_handler(CommandHandler("cookies", cookies))
    dp.add_handler(CommandHandler("grupos", ver))
    dp.add_handler(CommandHandler("agregargrupo", agregar_grupo))
    dp.add_handler(CommandHandler("borrargrupos", borrar_grupos))
    dp.add_handler(CommandHandler("activar", activar))
    dp.add_handler(CommandHandler("desactivar", desactivar))
    dp.add_handler(MessageHandler(Filters.photo, imagen))

    # Agrega programación automática
    scheduler = BackgroundScheduler()
    for hora in data['horarios']:
        h, m = map(int, hora.split(":"))
        scheduler.add_job(auto_publicar, 'cron', hour=h, minute=m)
    scheduler.start()

    updater.start_polling()
    print("Bot corriendo...")
    updater.idle()

if __name__ == '__main__':
    main()
