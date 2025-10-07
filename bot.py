import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# FAQ данные
FAQ = {
    'hours': '⏰ Мы работаем: Пн-Пт 9:00-18:00, Сб-Вс 10:00-16:00',
    'contact': '📞 Контакты:\n📧 Email: support@example.com\n📱 Телефон: +7 (XXX) XXX-XX-XX',
    'delivery': '🚚 Доставка: 2-5 рабочих дней по всей стране',
    'payment': '💳 Оплата: Наличные, карты, онлайн-переводы',
}

def log_user_message(update: Update):
    user = update.message.from_user
    text = update.message.text
    with open("users_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{user.first_name} ({user.username}) — {text}\n")


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⏰ Время работы", callback_data='hours')],
        [InlineKeyboardButton("📞 Контакты", callback_data='contact')],
        [InlineKeyboardButton("🚚 Доставка", callback_data='delivery')],
        [InlineKeyboardButton("💳 Оплата", callback_data='payment')],
        [InlineKeyboardButton("❓ Помощь", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    user_name = update.effective_user.first_name

    await update.message.reply_text(
        f'👋 Привет, {user_name}!\n\n'
        'Я бот поддержки клиентов.\n'
        'Выберите интересующий вас вопрос:',
        reply_markup=reply_markup
    )


# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        '📋 Доступные команды:\n\n'
        '/start - Главное меню\n'
        '/help - Показать эту справку\n'
        '/contact - Связаться с нами\n\n'
        'Или просто напишите ваш вопрос!'
    )
    await update.message.reply_text(help_text)


# Команда /contact
async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(FAQ['contact'])


# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        text = (
            '📋 Доступные команды:\n\n'
            '/start - Главное меню\n'
            '/help - Показать справку\n'
            '/contact - Связаться с нами\n\n'
            'Вы также можете написать ваш вопрос текстом!'
        )
    else:
        text = FAQ.get(query.data, 'Информация не найдена')

    # Кнопка "Назад в меню"
    keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup)


# Возврат в главное меню
async def back_to_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⏰ Время работы", callback_data='hours')],
        [InlineKeyboardButton("📞 Контакты", callback_data='contact')],
        [InlineKeyboardButton("🚚 Доставка", callback_data='delivery')],
        [InlineKeyboardButton("💳 Оплата", callback_data='payment')],
        [InlineKeyboardButton("❓ Помощь", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        '👋 Главное меню.\n\n'
        'Выберите интересующий вас вопрос:',
        reply_markup=reply_markup
    )


# Обработка текстовых сообщений
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_message(update)
    user_message = update.message.text.lower()

    # Простые автоответы
    if 'привет' in user_message or 'здравствуй' in user_message:
        await update.message.reply_text('👋 Привет! Чем могу помочь? Используйте /start для меню.')
    elif 'спасибо' in user_message:
        await update.message.reply_text('🙏 Пожалуйста! Обращайтесь!')
    elif 'время' in user_message or 'работа' in user_message:
        await update.message.reply_text(FAQ['hours'])
    elif 'контакт' in user_message or 'телефон' in user_message:
        await update.message.reply_text(FAQ['contact'])
    elif 'доставк' in user_message:
        await update.message.reply_text(FAQ['delivery'])
    elif 'оплат' in user_message or 'плат' in user_message:
        await update.message.reply_text(FAQ['payment'])
    else:
        await update.message.reply_text(
            '🤔 Я не совсем понял ваш вопрос.\n\n'
            'Используйте /start для выбора темы из меню!'
        )


def main():
    # Создаём приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("contact", contact_command))
    application.add_handler(CallbackQueryHandler(back_to_menu_handler, pattern='back_to_menu'))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Запускаем бота
    logger.info('Бот запущен!')
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()