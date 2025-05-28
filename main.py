import os
import time
import json
import logging
from datetime import datetime
from threading import Thread

from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler

from pytz import timezone
from facebook_poster import publicar_en_facebook
from utils import cargar_config, guardar_config
from keep_alive import keep_alive

# ── Configuración ─────────────────────────────────────────────────────────────
TOKEN     = os.getenv("TELEGRAM_TOKEN")
OWNER_ID  = int(os.getenv("TELEGRAM_USER_ID"))
DATA_FILE = "config.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Carga inicial de configuración ─────────────────────────────────────────────
config = cargar_config()

# ── Mantener vivo con Flask ────────────────────────────────────────────────────
keep_alive()

# ── Scheduler para publicación automática ─────────────────────────────────────
sched = BackgroundScheduler(timezone=timezone("America/Havana"))

def trabajo_automatico():
    if config.get("modo_auto") and config.get("texto") and config.get("grupos"):
        logger.info("💥 Ejecutando trabajo automático...")
        for grupo in config["grupos"]:
            logger.info(f"➡️ Publicando en: {grupo}")
            publicar_en_facebook(
                cookies=config["cookies"],
                grupo_url=grupo,
                mensaje=config["texto"],
                ruta_imagen=config.get("imagen")
            )
            time.sleep(20)
        Bot(token=TOKEN).send_message(chat_id=OWNER_ID, text="✅ Publicación automática completada.")

def schedule_auto():
    sched.remove_all_jobs()
    hora = config.get("hora", "08:00")
    h, m = map(int, hora.split(":"))
    sched.add_job(trabajo_automatico, "cron", hour=h, minute=m)
    sched.start()

schedule_auto()

# ── Handlers de Telegram ───────────────────────────────────────────────────────
updater = Updater(token=TOKEN, use_context=True)
dp = updater.dispatcher

def restricted(fn):
    def wrapper(update: Update, ctx: CallbackContext, *a, **k):
        if update.effective_user.id != OWNER_ID:
            return
        return fn(update, ctx, *a, **k)
    return wrapper

@restricted
def start(update, ctx):
    ctx.bot.send_message(chat_id=update.effective_chat.id, text="🤖 Bot activo. Usa /help para ver comandos.")
    logger.info("Bot iniciado (/start)")

@restricted
def help_cmd(update, ctx):
    ctx.bot.send_message(chat_id=update.effective_chat.id, text="""
/start           – Ver estado del bot
/help            – Mostrar esta ayuda
/set_text TEXTO  – Guardar texto de publicación
/set_image       – Enviar y guardar imagen
/set_cookies CK  – Guardar cookies de Facebook
/add_group URL   – Añadir grupo
/list_groups     – Listar grupos añadidos
/show_config     – Ver configuración actual
/set_time HH:MM  – Programar hora automática
/auto_on         – Activar publicación automática
/auto_off        – Desactivar publicación automática
/post_now        – Publicar manualmente ahora
""")

@restricted
def set_text(update, ctx):
    config["texto"] = " ".join(ctx.args)
    guardar_config(config)
    ctx.bot.send_message(chat_id=update.effective_chat.id, text="✅ Texto guardado.")

@restricted
def set_image(update, ctx):
    if update.message.photo:
        file = update.message.photo[-1].get_file()
        file.download("imagen.jpg")
        config["imagen"] = "imagen.jpg"
        guardar_config(config)
        ctx.bot.send_message(chat_id=update.effective_chat.id, text="✅ Imagen guardada.")
    else:
        ctx.bot.send_message(chat_id=update.effective_chat.id, text="❌ Envía una imagen junto al comando.")

@restricted
def set_cookies(update, ctx):
    config["cookies"] = " ".join(ctx.args)
    guardar_config(config)
    ctx.bot.send_message(chat_id=update.effective_chat.id, text="✅ Cookies guardadas.")

@restricted
def add_group(update, ctx):
    url = " ".join(ctx.args)
    config.setdefault("grupos", []).append(url)
    guardar_config(config)
    ctx.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Grupo añadido:\n{url}")

@restricted
def list_groups(update, ctx):
    grupos = config.get("grupos", [])
    if not grupos:
        ctx.bot.send_message(chat_id=update.effective_chat.id, text="No hay grupos añadidos.")
    else:
        texto = "\n".join(f"{i+1}. {g}" for i, g in enumerate(grupos))
        ctx.bot.send_message(chat_id=update.effective_chat.id, text=texto)

@restricted
def show_config(update, ctx):
    texto = config.get("texto", "<vacío>")
    imagen = "Sí" if config.get("imagen") else "No"
    cookies = "Sí" if config.get("cookies") else "No"
    grupos = config.get("grupos", [])
    hora = config.get("hora", "08:00")
    modo = "Activo" if config.get("modo_auto") else "Inactivo"
    resumen = (
        f"Texto: {texto}\nImagen: {imagen}\nCookies: {cookies}"
        f"\nModo auto: {modo}\nHora: {hora}\nGrupos:\n"
        + ("\n".join(f"{i+1}. {g}" for i, g in enumerate(grupos)) or "<ninguno>")
    )
    ctx.bot.send_message(chat_id=update.effective_chat.id, text=resumen)

@restricted
def set_time(update, ctx):
    t = ctx.args[0] if ctx.args else ""
    try:
        datetime.strptime(t, "%H:%M")
        config["hora"] = t
        guardar_config(config)
        schedule_auto()
        ctx.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Hora automática: {t}")
    except:
        ctx.bot.send_message(chat_id=update.effective_chat.id, text="❌ Formato inválido. Usa HH:MM")

@restricted
def auto_on(update, ctx):
    config["modo_auto"] = True
    guardar_config(config)
    schedule_auto()
    ctx.bot.send_message(chat_id=update.effective_chat.id, text="✅ Auto-publicación ACTIVADA.")

@restricted
def auto_off(update, ctx):
    config["modo_auto"] = False
    guardar_config(config)
    sched.remove_all_jobs()
    ctx.bot.send_message(chat_id=update.effective_chat.id, text="✅ Auto-publicación DESACTIVADA.")

@restricted
def post_now(update, ctx):
    trabajo_automatico()
    ctx.bot.send_message(chat_id=update.effective_chat.id, text="✅ Publicación manual ejecutada.")

# Registrar handlers
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help_cmd))
dp.add_handler(CommandHandler("set_text", set_text))
dp.add_handler(CommandHandler("set_image", set_image))
dp.add_handler(CommandHandler("set_cookies", set_cookies))
dp.add_handler(CommandHandler("add_group", add_group))
dp.add_handler(CommandHandler("list_groups", list_groups))
dp.add_handler(CommandHandler("show_config", show_config))
dp.add_handler(CommandHandler("set_time", set_time))
dp.add_handler(CommandHandler("auto_on", auto_on))
dp.add_handler(CommandHandler("auto_off", auto_off))
dp.add_handler(CommandHandler("post_now", post_now))
dp.add_handler(MessageHandler(Filters.photo, set_image))

# Iniciar polling
updater.start_polling()
updater.idle()
