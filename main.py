import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ✅ Token from Render Environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to ORION Marks Calculator!\n\n"
        "📩 Please send your SSC result HTML link.\n"
        "I will calculate your marks from it."
    )

def extract_marks_from_html(html_url):
    try:
        response = requests.get(html_url)
        soup = BeautifulSoup(response.content, "html.parser")

        correct = wrong = 0
        questions = soup.find_all("table", class_="menu-tbl")

        for q in questions:
            selected = q.find("td", class_="bordertbl selectedOption")
            correct_ans = q.find("td", class_="rightAnsOption")

            if selected and correct_ans:
                if selected.text.strip() == correct_ans.text.strip():
                    correct += 1
                else:
                    wrong += 1

        attempted = correct + wrong
        unattempted = 100 - attempted
        score = correct * 2 - wrong * 0.5
        accuracy = round((correct / attempted) * 100, 2) if attempted > 0 else 0

        return {
            "correct": correct,
            "wrong": wrong,
            "unattempted": unattempted,
            "score": score,
            "accuracy": accuracy
        }

    except Exception as e:
        return {"error": str(e)}

async def handle_html_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Please send a valid HTML link.")
        return

    await update.message.reply_text("🔍 Reading your result...")

    result = extract_marks_from_html(url)

    if "error" in result:
        await update.message.reply_text(f"❌ Error: {result['error']}")
    else:
        await update.message.reply_text(
            f"✅ Correct: {result['correct']}\n"
            f"❌ Wrong: {result['wrong']}\n"
            f"⭕ Unattempted: {result['unattempted']}\n\n"
            f"🧮 Score: {result['score']} / 200\n"
            f"📊 Accuracy: {result['accuracy']}%"
        )

def main():
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN is not set. Please check Render environment variables.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_html_link))
    app.run_polling()
