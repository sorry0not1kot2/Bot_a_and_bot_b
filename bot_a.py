import os
import sys

# Активация виртуального окружения
venv_path = os.path.join(os.getcwd(), 'venv', 'bin', 'activate_this.py')
if os.path.exists(venv_path):
    with open(venv_path) as f:
        exec(f.read(), dict(__file__=venv_path))

# Теперь можно импортировать другие модули и запускать бота
from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler, CallbackContext, Filters
import telegram.ext.filters as filters
from telegram import ParseMode

# Получение значений из переменных окружения
TOKEN_A = os.getenv('TOKEN_A')
GROUP_A_ID = int(os.getenv('GROUP_A_ID'))
GROUP_B_ID = int(os.getenv('GROUP_B_ID'))
BOT_A_USERNAME = os.getenv('BOT_A_USERNAME')
BOT_B_USERNAME = os.getenv('BOT_B_USERNAME')

# Создаем объект бота
bot_a = Bot(TOKEN_A)
updater_a = Updater(bot=bot_a)
dispatcher_a = updater_a.dispatcher

# Словарь для отслеживания соответствия между пересланными сообщениями и пользователями
user_message_mapping = {}

def forward_to_group_b(update: Update, context: CallbackContext):
    msg = update.message
    # Проверяем, что сообщение из группы A и адресовано боту A
    if msg.chat_id == GROUP_A_ID and BOT_A_USERNAME in msg.text:
        # Заменяем упоминание бота A на упоминание бота B
        text_for_bot_b = msg.text.replace(BOT_A_USERNAME, BOT_B_USERNAME)
        
        # Пересылаем сообщение в группу B и сохраняем соответствие между исходным сообщением и пересланным
        if msg.text:
            message = bot_a.send_message(chat_id=GROUP_B_ID, text=text_for_bot_b)
        elif msg.photo:
            message = bot_a.send_photo(chat_id=GROUP_B_ID, photo=msg.photo[-1].file_id, caption=text_for_bot_b)
        elif msg.video:
            message = bot_a.send_video(chat_id=GROUP_B_ID, video=msg.video.file_id, caption=text_for_bot_b)
        elif msg.document:
            message = bot_a.send_document(chat_id=GROUP_B_ID, document=msg.document.file_id, caption=text_for_bot_b)
        elif msg.audio:
            message = bot_a.send_audio(chat_id=GROUP_B_ID, audio=msg.audio.file_id, caption=text_for_bot_b)
        
        user_message_mapping[message.message_id] = msg.message_id

def reply_to_group_a(update: Update, context: CallbackContext):
    msg = update.message
    # Проверяем, что сообщение из группы B и является ответом от бота B
    if msg.chat_id == GROUP_B_ID and msg.reply_to_message and msg.reply_to_message.message_id in user_message_mapping:
        # Получаем ID исходного сообщения из группы A
        original_message_id = user_message_mapping[msg.reply_to_message.message_id]
        # Пересылаем ответное сообщение в группу A
        if msg.text:
            bot_a.send_message(chat_id=GROUP_A_ID, text=msg.text, reply_to_message_id=original_message_id)
        elif msg.photo:
            bot_a.send_photo(chat_id=GROUP_A_ID, photo=msg.photo[-1].file_id, caption=msg.caption, reply_to_message_id=original_message_id)
        elif msg.video:
            bot_a.send_video(chat_id=GROUP_A_ID, video=msg.video.file_id, caption=msg.caption, reply_to_message_id=original_message_id)
        elif msg.document:
            bot_a.send_document(chat_id=GROUP_A_ID, document=msg.document.file_id, caption=msg.caption, reply_to_message_id=original_message_id)
        elif msg.audio:
            bot_a.send_audio(chat_id=GROUP_A_ID, audio=msg.audio.file_id, caption=msg.caption, reply_to_message_id=original_message_id)
        
        # Удаляем сохраненный ID сообщения, так как ответ уже был отправлен
        del user_message_mapping[msg.reply_to_message.message_id]

# Добавляем обработчики сообщений
dispatcher_a.add_handler(MessageHandler(Filters.text & filters.Chat(GROUP_A_ID), forward_to_group_b))
dispatcher_a.add_handler(MessageHandler(Filters.photo & filters.Chat(GROUP_A_ID), forward_to_group_b))
dispatcher_a.add_handler(MessageHandler(Filters.video & filters.Chat(GROUP_A_ID), forward_to_group_b))
dispatcher_a.add_handler(MessageHandler(Filters.document & filters.Chat(GROUP_A_ID), forward_to_group_b))
dispatcher_a.add_handler(MessageHandler(Filters.audio & filters.Chat(GROUP_A_ID), forward_to_group_b))
dispatcher_a.add_handler(MessageHandler(Filters.text & filters.Chat(GROUP_B_ID), reply_to_group_a))
dispatcher_a.add_handler(MessageHandler(Filters.photo & filters.Chat(GROUP_B_ID), reply_to_group_a))
dispatcher_a.add_handler(MessageHandler(Filters.video & filters.Chat(GROUP_B_ID), reply_to_group_a))
dispatcher_a.add_handler(MessageHandler(Filters.document & filters.Chat(GROUP_B_ID), reply_to_group_a))
dispatcher_a.add_handler(MessageHandler(Filters.audio & filters.Chat(GROUP_B_ID), reply_to_group_a))

# Запускаем бота
updater_a.start_polling()
updater_a.idle()
