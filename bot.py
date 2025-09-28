from db import init_db, save_user_data, get_user_data
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes
)
from TOKEN import TOKEN
import requests
init_db()

# Клавиатура для следующего шага
def next_step_keyboard(commands):
    return ReplyKeyboardMarkup(
        [[command] for command in commands],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('''
Здравствуйте, это бот для регистрации. Чтобы зарегистрироваться, нужно ввести следующие данные в строгом порядке:
ФИО - /full_name
Дату рождения - /birth_date
Номер телефона - /phone
Email - /email

Для сохранения данных используйте команду /submit
Для просмотра сохранённых данных — /info
''', reply_markup=next_step_keyboard(["/full_name"]))

# Отдельные команды для ввода
async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting'] = 'full_name'
    await update.message.reply_text('Введите ваше ФИО:')

async def birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting'] = 'birth_date'
    await update.message.reply_text('Введите вашу дату рождения:')

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting'] = 'phone'
    await update.message.reply_text('Введите ваш номер телефона:')

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting'] = 'email'
    await update.message.reply_text('Введите ваш email:')

# Упрощённый ввод через текст
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    reply = update.message.reply_text

    if text.startswith("фио:"):
        context.user_data['full_name'] = update.message.text[4:].strip()
        await reply("ФИО сохранено. Теперь введите дату рождения:", reply_markup=next_step_keyboard(["/birth_date"]))
    elif text.startswith("дата:") or text.startswith("дата рождения:"):
        context.user_data['birth_date'] = update.message.text.split(":", 1)[1].strip()
        await reply("Дата рождения сохранена. Теперь введите номер телефона:", reply_markup=next_step_keyboard(["/phone"]))
    elif text.startswith("телефон:") or text.startswith("номер:"):
        context.user_data['phone'] = update.message.text.split(":", 1)[1].strip()
        await reply("Телефон сохранён. Теперь введите email:", reply_markup=next_step_keyboard(["/email"]))
    elif text.startswith("email:") or text.startswith("e-mail:"):
        context.user_data['email'] = update.message.text.split(":", 1)[1].strip()
        await reply("Email сохранён. Все данные введены, нажмите /submit для сохранения.", reply_markup=next_step_keyboard(["/submit"]))
    else:
        awaiting = context.user_data.get('awaiting')
        if awaiting:
            context.user_data[awaiting] = update.message.text.strip()
            context.user_data['awaiting'] = None

            next_cmds = {
                'full_name': ("/birth_date", "Теперь введите дату рождения:"),
                'birth_date': ("/phone", "Теперь введите номер телефона:"),
                'phone': ("/email", "Теперь введите email:"),
                'email': ("/submit", "Все данные введены, нажмите /submit для сохранения.")
            }

            next_command, message = next_cmds.get(awaiting, (None, "Данные сохранены."))

            await reply(
                f"{awaiting.replace('_', ' ').capitalize()} сохранено. {message}",
                reply_markup=next_step_keyboard([next_command]) if next_command else None
            )
        else:
            await reply(
                "Не удалось определить тип данных. Введите команду или используйте формат, например:\nФИО: Иванов Иван Иванович"
            )

# Команда /submit
async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    required = ['full_name', 'birth_date', 'phone', 'email']
    missing = [field for field in required if field not in data]

    if missing:
        await update.message.reply_text(f"Не хватает данных: {', '.join(missing)}. Введите их с помощью команд или напрямую.")
        return

    save_user_data(
        id=update.effective_user.id,
        full_name=data['full_name'],
        birth_date=data['birth_date'],
        phone=data['phone'],
        email=data['email']
    )
    await update.message.reply_text("✅ Данные успешно сохранены!", reply_markup=next_step_keyboard(["/info"]))
    context.user_data.clear()

# Команда /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = get_user_data(user_id)

    if data:
        full_name, birth_date, phone, email = data
        await update.message.reply_text(
            f"Ваши данные:\n"
            f"ФИО: {full_name}\n"
            f"Дата рождения: {birth_date}\n"
            f"Телефон: {phone}\n"
            f"E-mail: {email}"
        )
    else:
        await update.message.reply_text("Нет сохранённых данных. Используйте команды или текстовый ввод для регистрации.")

# Инициализация и запуск бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("full_name", full_name))
app.add_handler(CommandHandler("birth_date", birth_date))
app.add_handler(CommandHandler("phone", phone))
app.add_handler(CommandHandler("email", email))
app.add_handler(CommandHandler("submit", submit))
app.add_handler(CommandHandler("info", info))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.run_polling()