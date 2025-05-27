# main.py
import os
import json
import time
import threading
import requests
from datetime import datetime
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler

TELEGRAM_TOKEN = "8189807535:AAFj3CAkLrZ8IV_PoJbkem3VELyjZlAnPwg"
bot = Bot(token=TELEGRAM_TOKEN)

DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({
            "text": "",
            "image_url": "",
            "groups": [],
            "auto_enabled": True,
            "post_hours": ["08:00", "18:00"]
        }, f)

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def send_progress(context, chat_id, current, total):
    context.bot.send_message(chat_id=chat_id, text=f"Publicando en grupo {current}/{total}...")

def post_to_facebook(group_id, text, image_url):
    print(f"Publicando en grupo {group_id}...")
    time.sleep(5)  # Simula la publicación con un intervalo para evitar bloqueos
    return True

def auto_post_job(context: CallbackContext):
    data = load_data()
    if not data["auto_enabled"]:
        return

    now = datetime.now().strftime("%H:%M")
    if now not in data["post_hours"]:
        return

    text = data["text"]
    image_url = data["image_url"]
    groups = data["groups"]
    chat_id = context.job.context

    for idx, group_id in enumerate(groups):
        post_to_facebook(group_id, text, image_url)
        send_progress(context, chat_id, idx + 1, len(groups))

def start(update: Update, context: CallbackContext):
    update.message.reply_text("¡Bot activo y listo! Usa /help para ver los comandos.")

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("/set_text - Enviar texto
/set_image - Enviar imagen
/add_group ID
/remove_group ID
/list_groups
/enable_auto
/disable_auto
/set_hours 08:00,18:00")

def set_text(update: Update, context: CallbackContext):
    text = " ".join(context.args)
    data = load_data()
    data["text"] = text
    save_data(data)
    update.message.reply_text("Texto guardado.")

def set_image(update: Update, context: CallbackContext):
    if update.message.photo:
        file = update.message.photo[-1].get_file()
        file_path = file.download()
        image_url = f"https://example.com/path/to/{os.path.basename(file_path)}"  # Modifica según tu hosting
        data = load_data()
        data["image_url"] = image_url
        save_data(data)
        update.message.reply_text("Imagen guardada.")
    else:
        update.message.reply_text("Envía una imagen.")

def add_group(update: Update, context: CallbackContext):
    group_id = " ".join(context.args)
    data = load_data()
    if group_id not in data["groups"]:
        data["groups"].append(group_id)
        save_data(data)
    update.message.reply_text(f"Grupo {group_id} añadido.")

def remove_group(update: Update, context: CallbackContext):
    group_id = " ".join(context.args)
    data = load_data()
    if group_id in data["groups"]:
        data["groups"].remove(group_id)
        save_data(data)
    update.message.reply_text(f"Grupo {group_id} eliminado.")

def list_groups(update: Update, context: CallbackContext):
    data = load_data()
    grupos = "\n".join(data["groups"])
    update.message.reply_text(f"Grupos guardados:\n{grupos}")

def enable_auto(update: Update, context: CallbackContext):
    data = load_data()
    data["auto_enabled"] = True
    save_data(data)
    update.message.reply_text("Modo automático ACTIVADO.")

def disable_auto(update: Update, context: CallbackContext):
    data = load_data()
    data["auto_enabled"] = False
    save_data(data)
    update.message.reply_text("Modo automático DESACTIVADO.")

def set_hours(update: Update, context: CallbackContext):
    hours = " ".join(context.args).split(",")
    data = load_data()
    data["post_hours"] = hours
    save_data(data)
    update.message.reply_text(f"Horarios actualizados: {', '.join(hours)}")

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("set_text", set_text))
    dp.add_handler(MessageHandler(Filters.photo, set_image))
    dp.add_handler(CommandHandler("add_group", add_group))
    dp.add_handler(CommandHandler("remove_group", remove_group))
    dp.add_handler(CommandHandler("list_groups", list_groups))
    dp.add_handler(CommandHandler("enable_auto", enable_auto))
    dp.add_handler(CommandHandler("disable_auto", disable_auto))
    dp.add_handler(CommandHandler("set_hours", set_hours))

    chat_id = 51170296
    job_queue = updater.job_queue
    job_queue.run_repeating(auto_post_job, interval=60, first=5, context=chat_id)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
