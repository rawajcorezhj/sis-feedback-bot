import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# States
LANG, CHOOSING, PARENT_NAME, STUDENT_NAME, PHONE, CONTENT = range(6)

# CONFIG
PRINCIPAL_CHAT_ID = int(os.getenv("PRINCIPAL_CHAT_ID", "123456789"))  # Replace with Principal's ID

# Dictionary containing translations for English, Uzbek, and Russian
LANG_DATA = {
    "en": {
        "welcome": "Welcome to **Singapore International School** Parent Feedback Bot.\nPlease select your preferred language:",
        "lang_buttons": [["🇬🇧 English", "🇺🇿 O'zbekcha", "🇷🇺 Русский"]],
        "menu_prompt": "You selected **English**.\nPlease choose what you would like to submit:",
        "category_buttons": [["⚠️ Complaint", "💡 Recommendation"]],
        "parent_prompt": "You are submitting a **{category}**.\n\nPlease enter your **Full Name (Parent)**:",
        "student_prompt": "Please enter your **Child's Full Name and Class** (e.g., Aziz Rakhimov, Grade 8):",
        "phone_prompt": "Please provide your **Phone Number** (you can click the button below to share it securely):",
        "phone_button": "📱 Share Phone Number",
        "content_prompt": "Thank you. Now, please write down the details of your {category}:",
        "success": "✅ Thank you! Your feedback has been securely submitted to the school administration.",
        "caption": "🚨 New School {category} Received from parent: *{parent_name}*"
    },
    "uz": {
        "welcome": "**Singapore International School** ota-onalar fikr-mulohaza botiga xush kelibsiz.\nIltimos, tilni tanlang:",
        "lang_buttons": [["🇬🇧 English", "🇺🇿 O'zbekcha", "🇷🇺 Русский"]],
        "menu_prompt": "Siz **O'zbek tilini** tanladingiz.\nIltimos, murojaat turini tanlang:",
        "category_buttons": [["⚠️ Shikoyat (Complaint)", "💡 Tavsiya (Recommendation)"]],
        "parent_prompt": "Siz **{category}** yubormoqdasiz.\n\nIltimos, ota-onaning **F.I.Sh. (Ism va Familiyangiz)** ni kiriting:",
        "student_prompt": "Iltimos, farzandingizning **F.I.Sh. va sinfini** kiriting (masalan: Aziz Rahimov, 8-sinf):",
        "phone_prompt": "Iltimos, **telefon raqamingizni** kiriting (xavfsiz ulashish uchun pastdagi tugmani bosing):",
        "phone_button": "📱 Telefon raqamni ulashish",
        "content_prompt": "Rahmat. Endi {category} tafsilotlarini batafsil yozib yuboring:",
        "success": "✅ Rahmat! Sizning murojaatingiz maktab ma'muriyatiga muvaffaqiyatli yuborildi.",
        "caption": "🚨 Yangi {category} qabul qilindi. Ota-ona: *{parent_name}*"
    },
    "ru": {
        "welcome": "Добро пожаловать в бот обратной связи для родителей **Singapore International School**.\nПожалуйста, выберите язык:",
        "lang_buttons": [["🇬🇧 English", "🇺🇿 O'zbekcha", "🇷🇺 Русский"]],
        "menu_prompt": "Вы выбрали **Русский язык**.\nПожалуйста, выберите категорию обращения:",
        "category_buttons": [["⚠️ Жалоба", "💡 Рекомендация"]],
        "parent_prompt": "Вы отправляете **{category}**.\n\nПожалуйста, введите ваше **ФИО (Родителя)**:",
        "student_prompt": "Пожалуйста, введите **ФИО ребенка и класс** (например: Азиз Рахимов, 8 класс):",
        "phone_prompt": "Пожалуйста, укажите ваш **Номер телефона** (можно нажать кнопку ниже для быстрой отправки):",
        "phone_button": "📱 Поделиться номером",
        "content_prompt": "Спасибо. Теперь подробно опишите вашу {category}:",
        "success": "✅ Спасибо! Ваше обращение было успешно передано администрации школы.",
        "caption": "🚨 Получена новая {category} от родителя: *{parent_name}*"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [["🇬🇧 English", "🇺🇿 O'zbekcha", "🇷🇺 Русский"]]
    await update.message.reply_text(
        "Welcome to **Singapore International School**.\nPlease select your language / Tilni tanlang / Выберите язык:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
        parse_mode="Markdown"
    )
    return LANG

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if "English" in text:
        lang_code = "en"
    elif "O'zbekcha" in text:
        lang_code = "uz"
    elif "Русский" in text:
        lang_code = "ru"
    else:
        await update.message.reply_text("Please use the keyboard buttons to select a language.")
        return LANG

    context.user_data['lang'] = lang_code
    t = LANG_DATA[lang_code]

    await update.message.reply_text(
        t["menu_prompt"],
        reply_markup=ReplyKeyboardMarkup(t["category_buttons"], resize_keyboard=True, one_time_keyboard=True),
        parse_mode="Markdown"
    )
    return CHOOSING

async def choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    lang = context.user_data.get('lang', 'en')
    t = LANG_DATA[lang]

    if "Complaint" in text or "Шикоят" in text or "Жалоба" in text:
        context.user_data['category_key'] = "Complaint"
        category_name = "Complaint" if lang == "en" else ("Shikoyat" if lang == "uz" else "Жалоба")
    else:
        context.user_data['category_key'] = "Recommendation"
        category_name = "Recommendation" if lang == "en" else ("Tavsiya" if lang == "uz" else "Рекомендация")

    context.user_data['category_display'] = category_name

    await update.message.reply_text(
        t["parent_prompt"].format(category=category_name),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return PARENT_NAME

async def get_parent_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['parent_name'] = update.message.text
    lang = context.user_data.get('lang', 'en')
    t = LANG_DATA[lang]
    
    await update.message.reply_text(t["student_prompt"], parse_mode="Markdown")
    return STUDENT_NAME

async def get_student_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['student_info'] = update.message.text
    lang = context.user_data.get('lang', 'en')
    t = LANG_DATA[lang]
    
    keyboard = [[KeyboardButton(t["phone_button"], request_contact=True)]]
    await update.message.reply_text(
        t["phone_prompt"],
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
        parse_mode="Markdown"
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.contact:
        context.user_data['phone'] = update.message.contact.phone_number
    else:
        context.user_data['phone'] = update.message.text

    lang = context.user_data.get('lang', 'en')
    t = LANG_DATA[lang]
    cat_name = context.user_data['category_display']

    await update.message.reply_text(
        t["content_prompt"].format(category=cat_name.lower()),
        reply_markup=ReplyKeyboardRemove()
    )
    return CONTENT

async def get_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['content'] = update.message.text
    data = context.user_data
    lang = data.get('lang', 'en')
    t = LANG_DATA[lang]

    # Create formatted report text
    report_text = (
        f"====================================\n"
        f"SINGAPORE INTERNATIONAL SCHOOL REPORT\n"
        f"Type: {data['category_key']} ({data['category_display']})\n"
        f"Language Used: {lang.upper()}\n"
        f"====================================\n"
        f"Parent Name : {data['parent_name']}\n"
        f"Student Info: {data['student_info']}\n"
        f"Phone Number: {data['phone']}\n"
        f"------------------------------------\n"
        f"Details:\n{data['content']}\n"
        f"====================================\n"
    )

    filename = f"school_{data['category_key'].lower()}_{data['parent_name'].replace(' ', '_')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_text)

    # Success message to parent
    await update.message.reply_text(t["success"])

    # Send document (.txt file) to the Principal
    try:
        with open(filename, "rb") as f:
            await context.bot.send_document(
                chat_id=PRINCIPAL_CHAT_ID,
                document=f,
                caption=t["caption"].format(category=data['category_display'], parent_name=data['parent_name']),
                parse_mode="Markdown"
            )
    except Exception as e:
        logging.error(f"Failed to send report to principal: {e}")

    if os.path.exists(filename):
        os.remove(filename)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Cancelled / Bekor qilindi / Отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, language_handler)],
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choice_handler)],
            PARENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_parent_name)],
            STUDENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_student_name)],
            PHONE: [MessageHandler(filters.TEXT | filters.CONTACT, get_phone)],
            CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_content)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    print("Multi-language SIS Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()