import os
import json
import telebot
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ADMIN_ID = 7581985528
USERS_FILE = "users.json"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

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
                    "Sen O‘zbekiiston ta’lim tizimidagi ustozlarga yordam beruvchi GPT sun’iy intellekt modelsan. "
                    "Foydalanuvchilar umumiy o‘rta ta’lim maktablarida faoliyat yurituvchi o‘qituvchilardir. "
                    "Ular senga har qanday fan — matematika, fizika, kimyo, informatika, biologiya, adabiyot, tarix, ingliz tili va boshqa fanlar bo‘yicha savollar berishadi. "
                    "Savollar dars ishlanma, test savollar, metodik tavsiyalar, ta’limiy qonunlar, amaliy mashg‘ulotlar, elektron resurslar yoki mustaqil ishlar bo‘yicha bo‘lishi mumkin. "
                    "Javoblaringni faqat o‘zbek tilida yoz. Uslubing rasmiy, tushunarli, qisqa va aniq bo‘lishi zarur. "
                    "Hech qachon foydalanuvchi ismini, 'Salom', 'javob:', yoki 'men sizga shuni aytaman' kabi iboralarni yozma. "
                    "'Assalomu alaykum' iborasi faqat nutq yoki rasmiy murojaat so‘ralgandagina ishlatiladi. "
                    "Javobni mavzuga bevosita kirib boshlagin. Har doim o‘qituvchi savol berayotganini unutma."
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
        elif response.status_code == 401:
            return "❗ API kalit noto‘g‘ri yoki ishlamayapti. Iltimos, tekshiring."
        else:
            return f"[{response.status_code}] GPT javob bermadi."
    except Exception as e:
        return f"GPT bilan bog‘lanishda xatolik: {e}"

@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    save_user(user_id, name)
    bot.reply_to(message, f"Assalomu alaykum, {name}! Men ustozlar uchun sun’iy intellekt botman. Menga yozing, yordam beraman.")

@bot.message_handler(commands=['stat'])
def show_stats(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Bunday buyruq mavjud emas.")
        return

    if not os.path.exists(USERS_FILE):
        bot.reply_to(message, "Hozircha foydalanuvchilar ro‘yxati yo‘q.")
        return

    with open(USERS_FILE, 'r') as f:
        data = json.load(f)

    text = f"Bot foydalanuvchilari: {len(data)} ta\n\n"
    for uid, info in data.items():
        text += f"ID: {uid}\nIsm: {info['name']}\nOxirgi kirish: {info['last_seen']}\n\n"

    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    prompt = message.text.strip()

    save_user(user_id, name)
    bot.send_chat_action(message.chat.id, 'typing')

    javob = ask_gpt(prompt)
    bot.reply_to(message, javob)

print("Bot ishga tushdi...")

while True:
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        print(f"Polling xatolik: {e}")
