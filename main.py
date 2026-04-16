import telebot
import openai
import time
from datetime import datetime
from requests.exceptions import ReadTimeout, ConnectionError

# --- СІЗДІҢ МӘЛІМЕТТЕРІҢІЗ ҚОСЫЛДЫ ---
TOKEN = '8785253485:AAHpsup5Zr8uEEli1iseyn43k_V69VIzhLQ'
DEEPSEEK_API_KEY = 'sk-0ce2b33d2495486fae0994f06277ff96'
# ------------------------------------

bot = telebot.TeleBot(TOKEN)

# DeepSeek клиентін баптау
client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# Пайдаланушылардың хат-хабарлар тарихын сақтауға арналған сөздік
user_history = {}

def get_ai_response(user_id, user_text):
    # Ағымдағы уақытты алу (Бот уақытты білуі үшін)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Тарихты бастау және жүйелік нұсқаулық
    if user_id not in user_history:
        user_history[user_id] = [
            {"role": "system", "content": f"Сен Aqyl-AI роботысың. Қазіргі нақты уақыт: {current_time}. Сен ақылдысың және бәрін есте сақтайсың. Тек қазақ тілінде жауап бер."}
        ]
    
    # Пайдаланушы сөзін тарихқа қосу
    user_history[user_id].append({"role": "user", "content": user_text})
    
    # Контекстті (жадыны) соңғы 10 хабарламамен шектеу
    if len(user_history[user_id]) > 11:
        user_history[user_id] = [user_history[user_id][0]] + user_history[user_id][-10:]

    max_retries = 3
    for i in range(max_retries):
        try:
            print(f"DeepSeek-ке сұраныс жіберілуде... Талпыныс {i+1}")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=user_history[user_id],
                stream=False,
                timeout=60
            )
            answer = response.choices[0].message.content
            # Жауапты тарихқа сақтау
            user_history[user_id].append({"role": "assistant", "content": answer})
            return answer
        
        except (ReadTimeout, ConnectionError):
            if i < max_retries - 1:
                time.sleep(2)
                continue
            else:
                return "Кешіріңіз, байланыс үзілді. Сәлден соң қайталаңыз."
        except Exception as e:
            return f"Қате: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_history[user_id] = [] # Жаңадан бастағанда тарихты тазалау
    bot.reply_to(message, "Сәлем! Мен Aqyl-AI. Енді мен уақытты да, сіздің сөздеріңізді де ұмытпаймын. Не туралы сөйлесеміз?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = get_ai_response(message.chat.id, message.text)
    bot.reply_to(message, answer)

if __name__ == "__main__":
    print("Бот 'Есте сақтау' режимінде іске қосылды...")
    bot.polling(none_stop=True, timeout=90)
