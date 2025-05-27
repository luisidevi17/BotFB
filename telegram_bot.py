import yaml
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import subprocess

# Carga configuración def load_config():
    with open('config.yaml') as f:
        return yaml.safe_load(f)

def save_config(cfg):
    with open('config.yaml', 'w') as f:
        yaml.dump(cfg, f)

# Comandos def start(update: Update, context: CallbackContext):
    buttons = [
        [InlineKeyboardButton('Activar Automático', callback_data='auto_on'),
         InlineKeyboardButton('Desactivar Automático', callback_data='auto_off')]
    ]
    update.message.reply_text('Controla el bot:', reply_markup=InlineKeyboardMarkup(buttons))

# Callback de botones def button_cb(update: Update, context: CallbackContext):
    query = update.callback_query
    cfg = load_config()
    if query.data == 'auto_on':
        cfg['automatic'] = True
    else:
        cfg['automatic'] = False
    save_config(cfg)
    query.answer('Modo automático actualizado')

# Actualizar texto mañanay tarde def set_text(update: Update, context: CallbackContext):
    cfg = load_config()
    mode = context.args[0]  # 'morning' o 'evening'
    new_text = ' '.join(context.args[1:])
    cfg['content']['text'] = new_text
    save_config(cfg)
    update.message.reply_text(f'Texto de {mode} actualizado.')

# Recibe imágenes def image(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    path = f"{photo.file_id}.jpg"
    photo.get_file().download(path)
    cfg = load_config()
    cfg['content']['image'] = path
    save_config(cfg)
    update.message.reply_text('Imagen actualizada.')

# Estado de progreso
def status(update: Update, context: CallbackContext):
    # Lée log o estado y responde
    update.message.reply_text('Estado: listo para publicar.')

def main():
    cfg = load_config()
    updater = Updater(cfg['telegram']['token'], use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button_cb))
    dp.add_handler(CommandHandler('settext', set_text))
    dp.add_handler(CommandHandler('status', status))
    dp.add_handler(MessageHandler(Filters.photo, image))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()