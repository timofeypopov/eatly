print("🚀 Bot started and polling...")

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import openai
import base64
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#print(f"Loaded Telegram token: {TELEGRAM_TOKEN}")
# Создаем новый OpenAI client (новая версия SDK)
client = openai.OpenAI(api_key = OPENAI_API_KEY)

print("🤖 Bot ready...")

# Обработка текстов
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    print(f"Text from {user.id} ({user.username}): {text}")

# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_path = f"{user.id}_photo.jpg"
    await file.download_to_drive(file_path)
    print(f"📸 Photo from {user.id} saved as {file_path}")

    try:
        with open(file_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Ты — диетолог. Оцени по фото, сколько примерно калорий, белков, жиров и углеводов в блюде."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
        )

        result = response.choices[0].message.content
        await update.message.reply_text(f"🧠 Анализ блюда:\n\n{result}")

    except Exception as e:
        print(f"⚠️ Error while processing photo: {e}")
        await update.message.reply_text("⚠️ Не удалось обработать фото. Попробуй ещё раз чуть позже.")

# Запуск бота
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

app.run_polling()
