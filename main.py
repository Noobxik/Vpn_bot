import telebot
from telebot import types
import json
import logging



logging.basicConfig(
    level=logging.INFO,  # уровень логов: INFO, DEBUG, WARNING, ERROR
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot.log',  # все логи будут писаться в файл bot.log
    filemode='a'  # 'a' = добавлять в конец файла, 'w' = перезаписывать файл
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

bot = telebot.TeleBot(token='8435774037:AAFVncIwpCYkS8bqncS4iJlxzY7y19jyu6E')



def load_secrets():
    try:
        with open("secrets.json", "r") as f:
            data = json.load(f)
        logging.info("Секреты успешно загружены")
        return data
    except Exception as e:
        logging.error(f"Ошибка при загрузке secrets.json: {e}")
        return {}


def save_secrets(data):
    try:
        with open("secrets.json", "w") as f:
            json.dump(data, f, indent=4)
        logging.info("Секреты успешно сохранены")
    except Exception as e:
        logging.error(f"Ошибка при сохранении secrets.json: {e}")



def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Получить ключ")
    btn2 = types.KeyboardButton("Инструкция")
    btn3 = types.KeyboardButton("Помощь")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup



@bot.message_handler(commands=['start'])
def start(message):
    logging.info(f"Пользователь {message.from_user.username} ({message.chat.id}) запустил бота")
    markup = main_menu()
    bot.send_message(
        message.chat.id,
        f"Привет, <em>{message.from_user.username}</em>!\n"
        f"Введи <b>секретное слово</b>, и если оно верное — ты сможешь получить VPN-ключ.",
        parse_mode='HTML',
        reply_markup=markup
    )



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
    logging.info(f"Пользователь {message.from_user.username} ввел секретное слово: {secret_word}")
    secrets = load_secrets()

    if secret_word not in secrets:
        logging.warning(f"Секретное слово неверное: {secret_word} от {message.from_user.username}")
        markup = main_menu()
        bot.send_message(
            message.chat.id,
            "Секретное слово неверное или отсутствует в базе.\n"
            "Попробуй снова или воспользуйся меню ниже ",
            reply_markup=markup
        )
        return

    entry = secrets[secret_word]

    if entry.get("used"):
        logging.warning(f"Секретное слово уже использовано: {secret_word} от {message.from_user.username}")
        markup = main_menu()
        bot.send_message(
            message.chat.id,
            "⚠️ Это слово уже использовано.\n"
            "Попробуй другое или обратись за помощью:",
            reply_markup=markup
        )
        return

    vpn_key = entry["vpn_key"]
    logging.info(f"Секретное слово подтверждено для {message.from_user.username}: {secret_word}")



    bot.send_message(
        message.chat.id,
        f"Секретное слово подтверждено!\n\n"
        f"Твой VPN-ключ: <code>{vpn_key}</code>",
        parse_mode="HTML"
    )



    secrets[secret_word]["used"] = True
    secrets[secret_word]["user_id"] = message.from_user.id  # добавляем Telegram ID пользователя
    save_secrets(secrets)
    logging.info(f"Сохранен user_id {message.from_user.id} для ключа {secret_word}")


    entry = secrets[secret_word]

    if entry.get("used"):
        logging.warning(f"Секретное слово уже использовано: {secret_word} от {message.from_user.username}")
        markup = main_menu()
        bot.send_message(
            message.chat.id,
            "⚠️ Это слово уже использовано.\n"
            "Попробуй другое или обратись за помощью:",
            reply_markup=markup
        )
        return

    vpn_key = entry["vpn_key"]
    logging.info(f"Секретное слово подтверждено для {message.from_user.username}: {secret_word}")

    bot.send_message(
        message.chat.id,
        f"Секретное слово подтверждено!\n\n"
        f"Твой VPN-ключ: <code>{vpn_key}</code>",
        parse_mode="HTML"
    )

    secrets[secret_word]["used"] = True
    save_secrets(secrets)

logging.info("Бот успешно запущен")
bot.infinity_polling()
