import telebot
import openai
import time
from requests.exceptions import ReadTimeout, ConnectionError

# ПАРАМЕТРЛЕР
TOKEN = 'СІЗДІҢ_ТЕЛЕГРАМ_БОТ_ТОКЕНІҢІЗ'
DEEPSEEK_API_KEY = 'СІЗДІҢ_DEEPSEEK_API_КІЛТІҢІЗ'

bot = telebot.TeleBot(TOKEN)

# DeepSeek клиентін баптау
client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def get_ai_response(user_text):
    max_retries = 3  # Қайталау саны
    retry_delay = 2  # Күту уақыты (секунд)

    for i in range(max_retries):
        try:
            print(f"DeepSeek-ке сұраныс жіберілуде (Талпыныс {i+1})...")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Сен Aqyl-AI атты мектеп оқушыларына көмектесетін ақылды роботсың. Қазақ тілінде жауап бер."},
                    {"role": "user", "content": user_text},
                ],
                stream=False,
                timeout=60  # Күту уақытын 60 секундқа дейін ұзарттық
            )
            return response.choices[0].message.content
        
        except (ReadTimeout, ConnectionError):
            if i < max_retries - 1:
                print(f"Байланыс үзілді, {retry_delay} секундтан кейін қайта көреді...")
                time.sleep(retry_delay)
                continue
            else:
                return "Кешіріңіз, DeepSeek сервері қазір өте бос емес. Сәлден соң қайталап көріңізші."
        except Exception as e:
            return f"Қате орын алды: {str(e)}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Сәлем! Мен Aqyl-AI ботымын. Маған кез келген сұрағыңды қойсаң болады.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"Пайдаланушы: {message.from_user.first_name}, Сұрақ: {message.text}")
    
    # Бот "ойланып жатқан" секілді көрінуі үшін
    bot.send_chat_action(message.chat.id, 'typing')
    
    answer = get_ai_response(message.text)
    bot.reply_to(message, answer)

if __name__ == "__main__":
    print("Бот іске қосылды...")
    bot.polling(none_stop=True)
