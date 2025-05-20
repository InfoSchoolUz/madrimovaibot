import json
import os
import telebot
import requests
from dotenv import load_dotenv

# .env fayldan tokenlarni o‘qish
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
USERS_FILE = 'users.json'

# Foydalanuvchini saqlash
def save_user(user_id, name):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    with open(USERS_FILE, 'r') as f:
        data = json.load(f)
    if str(user_id) not in data:
        data[str(user_id)] = {"name": name}
        with open(USERS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

# Foydalanuvchi ismini olish
def get_username(user_id):
    if not os.path.exists(USERS_FILE):
        return "Do‘st"
    with open(USERS_FILE, 'r') as f:
        data = json.load(f)
    return data.get(str(user_id), {}).get("name", "Do‘st")

# GPT javobini olish
def ask_gpt(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"[{response.status_code}] GPT serveri javob bermadi."
    except Exception as e:
        return f"GPT bilan bog‘lanishda xatolik: {e}"

# /start komandasi
@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    save_user(user_id, name)
    bot.reply_to(message, f"Salom, {name}! Men sun’iy intellekt botman. Savol bering!")

# Har qanday xabarga javob
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    name = get_username(user_id)
    prompt = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    javob = ask_gpt(prompt)
    bot.reply_to(message, f"{name}, javob:\n{javob}")

# Botni ishga tushurish
while True:
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        print(f"Polling xatolik: {e}")
