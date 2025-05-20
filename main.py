
import os
import json
import telebot
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ADMIN_ID = 123456789  # Buni o'zingizning Telegram ID'ingiz bilan almashtiring

bot = telebot.TeleBot(TELEGRAM_TOKEN)
USERS_FILE = "users.json"

def save_user(user_id, name):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        data = json.load(f)

    data[str(user_id)] = {
        "name": name,
        "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_username(user_id):
    if not os.path.exists(USERS_FILE):
        return "DoвЂst"
    with open(USERS_FILE, "r") as f:
        data = json.load(f)
    return data.get(str(user_id), {}).get("name", "DoвЂst")

def ask_gpt(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Sen maktab informatika oвЂqituvchilari uchun yordam beruvchi GPT assistentsan. "
                    "Dars ishlanma, test savollar, IT mashgвЂulotlar, metodik koвЂrsatmalar, va OвЂzbekiston taвЂ™lim tizimidagi qonun-qoidalarga oid savollarga javob berasan. "
                    "Javoblarni oвЂzbek tilida yoz. Foydalanuvchi ismini hech qachon yozma. "
                    "'Azamat', 'javob:', 'Hurmatli foydalanuvchi' degan iboralarsiz, mavzuga bevosita javob ber."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"[{response.status_code}] GPT javob bermadi."
    except Exception as e:
        return f"GPT bilan bogвЂlanishda xatolik: {e}"

@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    save_user(user_id, name)
    bot.reply_to(message, f"Salom, {name}! Men ustozlar uchun sunвЂ™iy intellekt botman. Menga yozing, yordam beraman!")

@bot.message_handler(commands=['stat'])
def show_stats(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Kechirasiz, bu buyruq faqat admin uchun.")
        return

    if not os.path.exists(USERS_FILE):
        bot.reply_to(message, "Statistika mavjud emas.")
        return

    with open(USERS_FILE, 'r') as f:
        data = json.load(f)

    total_users = len(data)
    text = f"Botdan foydalanuvchilar soni: {total_users} ta\n\n"
    for uid, info in data.items():
        text += f"{info['name']} вЂ” oxirgi kirish: {info['last_seen']}\n"

    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    prompt = message.text.strip().lower()

    save_user(user_id, name)
    bot.send_chat_action(message.chat.id, 'typing')

    if prompt in ["salom", "assalomu alaykum", "hi", "hello"]:
        javob = f"Salom, {name}!"
    else:
        javob = ask_gpt(message.text)

    bot.reply_to(message, javob)

print("Bot ishga tushdi...")

while True:
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        print(f"Polling xatolik: {e}")
