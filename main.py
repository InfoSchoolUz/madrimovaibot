import telebot
from dotenv import load_dotenv
import os
import requests

# .env faylini yuklash
load_dotenv()

# Tokenlar
TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Telegram bot
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    text = f"Assalomu alaykum, {name}! Men ustozlar uchun sun’iy intellekt botman. Menga yozing, yordam beraman."
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    try:
        javob = get_ai_response(user_input)
        bot.send_message(message.chat.id, javob)
    except Exception as e:
        bot.send_message(message.chat.id, f"Xatolik yuz berdi: {e}")

def get_ai_response(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "Sen ustozlarga yordam beradigan intellektual yordamchisan."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    response = requests.post(url, headers=headers, json=data)
    try:
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        elif "error" in result:
            return f"OpenRouter xatosi: {result['error'].get('message', 'Nomaʼlum xato')}"
        else:
            return "Xatolik: AI javobi olinmadi."
    except Exception as e:
        return f"JSON xatosi: {e}"

print("Bot ishga tushdi...")
bot.remove_webhook()
bot.infinity_polling(threaded=False)
