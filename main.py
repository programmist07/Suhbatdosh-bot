from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, Application
import os
import json
from datetime import datetime
from telegram import Update

async def save_user_data(update: Update, text: str):
    user = update.effective_user

    if update.message and update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = "Telefon yo'q"

    data = {
        "user_id": user.id,
        "username": user.username or "Username yo'q",
        "name": user.full_name,
        "phone": phone,
        "text": text,
        "time": datetime.now().strftime("%c")
    }


    file_name = "user.json"


    if os.path.exists(file_name):
        with open(file_name, "r") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    existing_data.append(data)

    with open(file_name, "w") as file:
        json.dump(existing_data, file, indent=4)
        file.write("\n\n")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inline_buttons = [
        [InlineKeyboardButton("Salomlashuv", callback_data="salom")],
        [InlineKeyboardButton("Bugungi sana", callback_data="sana")],
        [InlineKeyboardButton("Tasodifiy fakt", callback_data="fakt")]
    ]

    inline_keyboard = InlineKeyboardMarkup(inline_buttons)

    reply_buttons = [
        [KeyboardButton("Telefon raqamni ulashish", request_contact=True)],
        ["Shaxsiy tabrik", "Ovqat tavsiya"]
    ]

    reply_keyboard = ReplyKeyboardMarkup(reply_buttons, resize_keyboard=True)

    await update.message.reply_text("<b>Inline va Reply keyboard tugmalardan foydalanishingiz mumkin</b>",
                                    parse_mode='HTML',
                                    reply_markup=reply_keyboard)
    await update.message.reply_text("<b>Inline keyboard tugmalari</b>",parse_mode='HTML', reply_markup=inline_keyboard)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        await save_user_data(update, query.data)

        if query.data == "salom":
            await query.edit_message_text("Salom botimizga xush kelibsiz!")
        elif query.data == "sana":
            await query.edit_message_text(f"Bugungi sana: {datetime.now().strftime('%Y-%m-%d')}")
        elif query.data == "fakt":
            await query.edit_message_text("Tasodifiy fakt: Bir kunda 86400 soniya bor")
    except Exception as e:
        print(f"Button handler error: {e}")

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        await save_user_data(update, "Telefon raqamini ulashdi")
        await update.message.reply_text("Rahmat! Telefon raqamingiz qabul qilindi.")
    else:
        await update.message.reply_text("Telefon raqamni ulashishda xatolik yuz berdi.")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        await save_user_data(update, update.message.text)

        if update.message.contact:
            await get_contact(update, context)

        tekst = update.message.text

        if tekst.lower() == "shaxsiy tabrik":
            await update.message.reply_text("Tabrik! Siz bizning botimizdan foydalanayapsiz!")
        elif tekst.lower() == "ovqat tavsiya":
            await update.message.reply_text("Bugun burger yoki pizza yeyishni tavsiya qilamiz!")
        else:
            await update.message.reply_text("Ma'lumot saqlandi!")
    else:
        await update.message.reply_text("Siz xabar yubormadingiz yoki noto'g'ri ma'lumot yubordingiz!")


application = ApplicationBuilder().token("7683580444:AAEhOvHHiTflRieeqkKBC3wyCGf7dzwQ9lU").build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.CONTACT, text_handler))

application.run_polling()