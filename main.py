import telebot
from telebot import types
import json

bot = telebot.TeleBot(token='8435774037:AAFVncIwpCYkS8bqncS4iJlxzY7y19jyu6E')

#json ключи
def load_secrets():
    with open("secrets.json", "r") as f:
        return json.load(f)


def save_secrets(data):
    with open("secrets.json", "w") as f:
        json.dump(data, f, indent=4)

#меню с ключами
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Получить ключ")
    btn2 = types.KeyboardButton("Инструкция")
    btn3 = types.KeyboardButton("Помощь")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup

#команда старт
@bot.message_handler(commands=['start'])
def start(message):
    markup = main_menu()
    bot.send_message(
        message.chat.id,
        f"Привет, <em>{message.from_user.username}</em>!\n"
        f"Введи <b>секретное слово</b>, и если оно верное — ты сможешь получить VPN-ключ.",
        parse_mode='HTML',
        reply_markup=markup
    )

#кнопка получения ключа
@bot.message_handler(func=lambda message: message.text == "Получить ключ")
def ask_secret(message):
    msg = bot.send_message(message.chat.id, "Введите своё секретное слово:")
    bot.register_next_step_handler(msg, check_secret)

#кнопка инструкции
@bot.message_handler(func=lambda message: message.text == "Инструкция")
def send_instruction(message):
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

#кнопка помощь
@bot.message_handler(func=lambda message: message.text == "Помощь")
def help_button(message):
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
    secrets = load_secrets()

    # Если кодовое слово не найдено
    if secret_word not in secrets:
        markup = main_menu()
        bot.send_message(
            message.chat.id,
            "❌ Секретное слово неверное или отсутствует в базе.\n"
            "Попробуй снова или воспользуйся меню ниже 👇",
            reply_markup=markup
        )
        return

    entry = secrets[secret_word]

    if entry.get("used"):
        markup = main_menu()
        bot.send_message(
            message.chat.id,
            "⚠️ Это слово уже использовано.\n"
            "Попробуй другое или обратись за помощью:",
            reply_markup=markup
        )
        return

    vpn_key = entry["vpn_key"]

    bot.send_message(
        message.chat.id,
        f"✅ Секретное слово подтверждено!\n\n"
        f"Твой VPN-ключ: <code>{vpn_key}</code>",
        parse_mode="HTML"
    )

    secrets[secret_word]["used"] = True
    save_secrets(secrets)


print("Бот успешно запущен")
bot.infinity_polling()
