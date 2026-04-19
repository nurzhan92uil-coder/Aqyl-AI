import logging
import datetime
import fitz  # PyMuPDF
import os
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- БАПТАУЛАР ---
TELEGRAM_TOKEN = "8785253485:AAHpsup5Zr8uEEli1iseyn43k_V69VIzhLQ"
GROQ_API_KEY = "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"

# Оқулықтар тізімі
BOOKS = ["6 кл.pdf", "8кл.pdf", "9 кл.pdf", "10 кл.pdf", "11 кл.pdf"]

client = Groq(api_key=GROQ_API_KEY)
user_history = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ІЗДЕУ ФУНКЦИЯСЫ ---
def search_in_all_books(query):
    combined_context = ""
    found_any = False
    keywords = [word.lower() for word in query.split() if len(word) > 3]
    
    for book_path in BOOKS:
        if os.path.exists(book_path):
            try:
                doc = fitz.open(book_path)
                found_in_this_book = 0
                for page_num, page in enumerate(doc):
                    text = page.get_text()
                    if any(kw in text.lower() for kw in keywords):
                        combined_context += f"\n[{book_path}, {page_num+1}-бет]:\n{text}\n"
                        found_any = True
                        found_in_this_book += 1
                    if found_in_this_book >= 2: break
                doc.close()
            except: pass
        if len(combined_context) > 5000: break
    return combined_context, found_any

def get_ai_response(user_id, user_text):
    now = datetime.datetime.now()
    current_date = now.strftime("%d.%m.%Y")
    days_kz = ["Дүйсенбі", "Сейсенбі", "Сәрсенбі", "Бейсенбі", "Жұма", "Сенбі", "Жексенбі"]
    weekday = days_kz[now.weekday()]

    book_info, info_found = search_in_all_books(user_text)

    if user_id not in user_history:
        user_history[user_id] = [
            {
                "role": "system", 
                "content": (
                    f"Бүгін: {current_date}, {weekday}. Сен — Ағыбаев Нұржан жасап шығарған көмекшісің. "
                    "Сенің стилің: қарапайым, сыпайы және нақты. "
                    "1. Өзіңді мақтама, 'білімдімін' деп айтпа. Тек сұраққа жауап бер. "
                    "2. Кез келген тақырыпта (ауа райы, жалпы сұрақтар) жауап беруге тырыс. 'Білмеймін' деп жауаптан қашпа. "
                    "3. Егер оқулықтан мәлімет табылса, оны пайдалан. Бірақ 'тек информатиканы білемін' деп пайдаланушыны шектеме. "
                    "4. Автор туралы сұраса: 'Мені Ағыбаев Нұржан есімді ұстаз құрастырған' деп қысқа қайыр."
                )
            }
        ]

    if info_found:
        prompt = f"Оқулық мәліметі бойынша жауап бер:\n{book_info}\n\nСұрақ: {user_text}"
    else:
        prompt = user_text

    user_history[user_id].append({"role": "user", "content": prompt})

    if len(user_history[user_id]) > 10:
        user_history[user_id] = [user_history[user_id][0]] + user_history[user_id][-9:]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=user_history[user_id]
        )
        return completion.choices[0].message.content
    except:
        return "Кешіріңіз, байланыс үзілді. Қайта жазып көріңізші."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply_text = get_ai_response(user_id, user_text)
    await update.message.reply_text(reply_text)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("РОБОТ ҚОСЫЛДЫ! Енді ол бәріне келісіммен жауап береді.")
    app.run_polling(drop_pending_updates=True)
