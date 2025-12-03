import telebot
from telebot import types
import json
import logging
from config import BOT_TOKEN, ADMIN_ID, SECRETS_FILE, LOG_FILE

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
    filemode='a'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

bot = telebot.TeleBot(token=BOT_TOKEN)

# Словарь для отслеживания состояния админа
admin_state = {}

# ==================== ФУНКЦИИ РАБОТЫ С ДАННЫМИ ====================

def load_secrets():
    try:
        with open(SECRETS_FILE, "r", encoding='utf-8') as f:
            data = json.load(f)
        logging.info("Секреты успешно загружены")
        return data
    except Exception as e:
        logging.error(f"Ошибка при загрузке {SECRETS_FILE}: {e}")
        return {}

def save_secrets(data):
    try:
        with open(SECRETS_FILE, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info("Секреты успешно сохранены")
    except Exception as e:
        logging.error(f"Ошибка при сохранении {SECRETS_FILE}: {e}")

# ==================== МЕНЮ ====================

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Получить ключ")
    btn2 = types.KeyboardButton("Инструкция")
    btn3 = types.KeyboardButton("Помощь")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup

def admin_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить ключ")
    btn2 = types.KeyboardButton("Просмотреть ключи")
    btn3 = types.KeyboardButton("Удалить ключ")
    btn4 = types.KeyboardButton("Выход из админки")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

# ==================== ОСНОВНЫЕ КОМАНДЫ ====================

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    username = message.from_user.username or "Гость"
    
    logging.info(f"Пользователь {username} ({chat_id}) запустил бота")
    
    if chat_id == ADMIN_ID:
        bot.send_message(
            chat_id,
            f"Привет, <em>{username}</em> (АДМИНИСТРАТОР)!\n"
            f"Выбери действие:",
            parse_mode='HTML',
            reply_markup=admin_menu()
        )
        admin_state[chat_id] = 'menu'
    else:
        markup = main_menu()
        bot.send_message(
            chat_id,
            f"Привет, <em>{username}</em>!\n"
            f"Введи <b>секретное слово</b>, и если оно верное — ты сможешь получить VPN-ключ.",
            parse_mode='HTML',
            reply_markup=markup
        )

# ==================== ПОЛЬЗОВАТЕЛЬСКИЕ КОМАНДЫ ====================

@bot.message_handler(func=lambda message: message.text == "Получить ключ")
def ask_secret(message):
    logging.info(f"Пользователь {message.from_user.username} запросил ключ")
    msg = bot.send_message(message.chat.id, "Введите своё секретное слово:")
    bot.register_next_step_handler(msg, check_secret)

@bot.message_handler(func=lambda message: message.text == "Инструкция")
def send_instruction(message):
    logging.info(f"Пользователь {message.from_user.username} запросил инструкцию")
    inline_markup = types.InlineKeyboardMarkup()
    btn_instr = types.InlineKeyboardButton(
        text="📘 Открыть инструкцию",
        url="https://telegra.ph/Instrukciya-11-03-27"
    )
    inline_markup.add(btn_instr)
    bot.send_message(
        message.chat.id,
        "Вот ссылка на инструкцию:",
        reply_markup=inline_markup
    )

@bot.message_handler(func=lambda message: message.text == "Помощь")
def help_button(message):
    logging.info(f"Пользователь {message.from_user.username} запросил помощь")
    inline_markup = types.InlineKeyboardMarkup()
    btn_help = types.InlineKeyboardButton(
        text="Связаться с поддержкой 💬",
        url="https://t.me/noobxik"
    )
    inline_markup.add(btn_help)
    bot.send_message(
        message.chat.id,
        "Если у тебя возникли проблемы — нажми кнопку ниже, чтобы связаться с поддержкой:",
        reply_markup=inline_markup
    )

def check_secret(message):
    secret_word = message.text.strip()
    chat_id = message.chat.id
    username = message.from_user.username or "Гость"
    
    logging.info(f"Пользователь {username} ввел секретное слово: {secret_word}")
    
    secrets = load_secrets()
    
    if secret_word not in secrets:
        logging.warning(f"Секретное слово неверное: {secret_word} от {username}")
        markup = main_menu()
        bot.send_message(
            chat_id,
            "Секретное слово неверное или отсутствует в базе.\n"
            "Попробуй снова или воспользуйся меню ниже ",
            reply_markup=markup
        )
        return
    
    entry = secrets[secret_word]
    
    if entry.get("used"):
        logging.warning(f"Секретное слово уже использовано: {secret_word} от {username}")
        markup = main_menu()
        bot.send_message(
            chat_id,
            "⚠️ Это слово уже использовано.\n"
            "Попробуй другое или обратись за помощью:",
            reply_markup=markup
        )
        return
    
    vpn_key = entry["vpn_key"]
    logging.info(f"Секретное слово подтверждено для {username}: {secret_word}")
    
    bot.send_message(
        chat_id,
        f"Секретное слово подтверждено!\n\n"
        f"Твой VPN-ключ: <code>{vpn_key}</code>",
        parse_mode="HTML"
    )
    
    # Обновляем данные ключа
    secrets[secret_word]["used"] = True
    secrets[secret_word]["user_id"] = message.from_user.id
    secrets[secret_word]["username"] = username
    save_secrets(secrets)
    logging.info(f"Сохранен user_id {message.from_user.id} и username {username} для ключа {secret_word}")

# ==================== АДМИН КОМАНДЫ ====================

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text == "Добавить ключ")
def add_key_start(message):
    chat_id = message.chat.id
    admin_state[chat_id] = 'waiting_secret'
    bot.send_message(chat_id, "Введите секретное слово для нового ключа:")

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and admin_state.get(message.chat.id) == 'waiting_secret')
def add_key_secret(message):
    chat_id = message.chat.id
    secret_word = message.text.strip()
    
    secrets = load_secrets()
    if secret_word in secrets:
        bot.send_message(chat_id, "❌ Это секретное слово уже существует!")
        admin_state[chat_id] = 'menu'
        return
    
    admin_state[chat_id] = 'waiting_vpn'
    admin_state[f"{chat_id}_secret"] = secret_word
    bot.send_message(chat_id, "Введите VPN-ключ:")

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and admin_state.get(message.chat.id) == 'waiting_vpn')
def add_key_vpn(message):
    chat_id = message.chat.id
    vpn_key = message.text.strip()
    secret_word = admin_state.get(f"{chat_id}_secret")
    
    admin_state[chat_id] = 'waiting_nickname'
    admin_state[f"{chat_id}_vpn"] = vpn_key
    bot.send_message(chat_id, "Введите никнейм/название для этого ключа:")

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and admin_state.get(message.chat.id) == 'waiting_nickname')
def add_key_nickname(message):
    chat_id = message.chat.id
    nickname = message.text.strip()
    secret_word = admin_state.get(f"{chat_id}_secret")
    vpn_key = admin_state.get(f"{chat_id}_vpn")
    
    secrets = load_secrets()
    secrets[secret_word] = {
        "vpn_key": vpn_key,
        "nickname": nickname,
        "used": False,
        "user_id": None,
        "username": None
    }
    save_secrets(secrets)
    
    logging.info(f"Администратор добавил новый ключ: {secret_word} ({nickname})")
    bot.send_message(
        chat_id,
        f"✅ Ключ успешно добавлен!\n\n"
        f"Секретное слово: <code>{secret_word}</code>\n"
        f"VPN-ключ: <code>{vpn_key}</code>\n"
        f"Никнейм: {nickname}",
        parse_mode='HTML',
        reply_markup=admin_menu()
    )
    
    # Очищаем состояние
    admin_state[chat_id] = 'menu'
    del admin_state[f"{chat_id}_secret"]
    del admin_state[f"{chat_id}_vpn"]

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text == "Просмотреть ключи")
def view_keys(message):
    chat_id = message.chat.id
    secrets = load_secrets()
    
    if not secrets:
        bot.send_message(chat_id, "❌ Нет сохраненных ключей", reply_markup=admin_menu())
        return
    
    text = "📋 <b>Все ключи:</b>\n\n"
    for secret, data in secrets.items():
        status = "✅ Использован" if data.get("used") else "❌ Не использован"
        username = data.get("username", "Не известен")
        nickname = data.get("nickname", "Без названия")
        
        text += (
            f"<b>Секретное слово:</b> <code>{secret}</code>\n"
            f"<b>Никнейм:</b> {nickname}\n"
            f"<b>VPN-ключ:</b> <code>{data['vpn_key']}</code>\n"
            f"<b>Статус:</b> {status}\n"
            f"<b>Пользователь:</b> {username}\n\n"
        )
    
    bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=admin_menu())

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text == "Удалить ключ")
def delete_key_start(message):
    chat_id = message.chat.id
    admin_state[chat_id] = 'waiting_delete'
    bot.send_message(chat_id, "Введите секретное слово ключа для удаления:")

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and admin_state.get(message.chat.id) == 'waiting_delete')
def delete_key(message):
    chat_id = message.chat.id
    secret_word = message.text.strip()
    
    secrets = load_secrets()
    if secret_word not in secrets:
        bot.send_message(chat_id, "❌ Ключ не найден!", reply_markup=admin_menu())
        admin_state[chat_id] = 'menu'
        return
    
    del secrets[secret_word]
    save_secrets(secrets)
    
    logging.info(f"Администратор удалил ключ: {secret_word}")
    bot.send_message(chat_id, f"✅ Ключ <code>{secret_word}</code> успешно удален!", parse_mode='HTML', reply_markup=admin_menu())
    admin_state[chat_id] = 'menu'

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.text == "Выход из админки")
def exit_admin(message):
    chat_id = message.chat.id
    admin_state[chat_id] = None
    bot.send_message(chat_id, "Вы вышли из админки", reply_markup=main_menu())

# ==================== ЗАПУСК БОТА ====================

if __name__ == '__main__':
    logging.info("Бот успешно запущен")
    bot.infinity_polling()
