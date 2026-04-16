import telebot
import requests
import json
import urllib3

# SSL қатесі туралы ескертулерді көрсетпеу үшін
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- КІЛТТЕР ---
TELEGRAM_TOKEN = "8785253485:AAHpsup5Zr8uEEli1iseyn43k_V69VIzhLQ"
DEEPSEEK_KEY = "sk-0ce2b33d2495486fae0994f06277ff96"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_deepseek_response(text):
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_KEY}"
    }
    
    system_instruction = (
        "Сен - Ағыбаев Нұржан құрастырған ақылды жасанды интеллект көмекшісісің. "
        "Сенің есімің - 'Aqyl-AI'. Егер біреу 'Сені кім жасады?' деп сұраса, "
        "міндетті түрде: 'Мені Ағыбаев Нұржан құрастырып шығарды' деп жауап бер."
    )
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": text}
        ]
    }
    
    try:
        # verify=False параметрін қостық - бұл SSL сертификатын тексеруді айналып өтеді
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"DeepSeek қатесі: {response.status_code}"
            
    except Exception as e:
        return f"Байланыс қатесі: {e}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"Сұрақ: {message.text}")
    bot.send_chat_action(message.chat.id, 'typing')
    answer = get_deepseek_response(message.text)
    bot.reply_to(message, answer)
    print("Жауап жіберілді!")

print("-----------------------------------------")
print("AQYL-AI БОТЫ SSL ҚАТЕСІ ТҮЗЕТІЛІП ҚОСЫЛДЫ!")
print("-----------------------------------------")

bot.infinity_polling()
