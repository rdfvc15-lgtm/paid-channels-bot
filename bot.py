import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Получение переменных окружения
BOT_TOKEN = os.getenv('8219637282:AAHRLrbUwmPe4LaVe8msPKCKev_MdANDT4E')
ADMIN_ID = os.getenv('473189755')

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не установлен! Проверьте переменные окружения в Railway.")

logger.info("✅ Бот инициализирован, проверяем переменные...")

# Данные о каналах
CHANNELS = {
    "free": {
        "name": "Бесплатный канал Эли",
        "url": "https://t.me/ElyaEduardovna777",
        "price": 0
    },
    "remote_work": {
        "name": "Доход на удаленке",
        "url": "https://t.me/+tA3a1ehNHLg2MmVi", 
        "price": 2000,
        "description": "Канал 'Доход на удаленке' - заработок с нуля"
    },
    "training": {
        "name": "Тренировки", 
        "url": "https://t.me/+D4OA6TJlY0YwMGYy",
        "price": 2000,
        "description": "Канал по тренировкам"
    }
}

CARD_DETAILS = """
💳 **Реквизиты для оплаты:**

🏦 Банк: Альфа банк
📱 Номер карты: `2200 1545 6517 5188`
👤 Получатель: Зульфия Юлбарисова

💵 Сумма: 2000 руб.
📝 Назначение: Оплата доступа к каналу
"""

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Меню выбора каналов
def get_channels_keyboard():
    keyboard = InlineKeyboardBuilder()
    
    keyboard.add(InlineKeyboardButton(
        text="🎁 Бесплатный канал Эли", 
        url=CHANNELS["free"]["url"]
    ))
    
    keyboard.add(InlineKeyboardButton(
        text="💼 Доход на удаленке - 2000 руб.", 
        callback_data="buy_remote_work"
    ))
    
    keyboard.add(InlineKeyboardButton(
        text="💪 Тренировки - 2000 руб.", 
        callback_data="buy_training"
    ))
    
    keyboard.adjust(1)
    return keyboard.as_markup()

def get_payment_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="📤 Отправить реквизиты перевода", 
        callback_data="send_receipt"
    ))
    return keyboard.as_markup()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = """
🤖 **Добро пожаловать!**

Здесь вы можете получить доступ к полезным Telegram каналам:

🎁 **Бесплатный канал** - интересный контент без оплаты
💼 **Платные каналы** - эксклюзивные материалы за 2000 руб.

👇 Выберите интересующий канал:
    """
    
    await message.answer(welcome_text, reply_markup=get_channels_keyboard())
    logger.info(f"Пользователь {message.from_user.id} запустил бота")

@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery):
    channel_type = callback.data.split("_")[1]
    channel = CHANNELS.get(channel_type)
    
    if not channel:
        await callback.answer("Канал не найден")
        return
    
    text = f"""
💰 **Оплата доступа к каналу**

📢 **Название:** {channel['name']}
💵 **Стоимость:** {channel['price']} руб.
📝 **Описание:** {channel.get('description', '')}

{CARD_DETAILS}

⚠️ **Инструкция:**
1. Переведите {channel['price']} руб. на указанную карту
2. Нажмите кнопку «Отправить реквизиты перевода»
3. Пришлите скриншот или данные перевода
4. После проверки вы получите доступ к каналу
    """
    
    await callback.message.edit_text(text, reply_markup=get_payment_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "send_receipt")
async def request_receipt(callback: types.CallbackQuery):
    text = """
📤 **Отправьте реквизиты перевода**

Пожалуйста, отправьте:
• Скриншот перевода
• Или дату и время перевода
• Или сумму и последние 4 цифры карты отправителя

Админ проверит платеж и добавит вас в канал в течение 24 часов.
    """
    
    await callback.message.answer(text)
    await callback.answer()

@dp.message(F.content_type.in_({'photo', 'document'}))
async def handle_media(message: types.Message):
    user_info = f"Пользователь: @{message.from_user.username or 'нет'} ({message.from_user.id})"
    
    admin_text = f"""
🎯 **Новый платеж!**

{user_info}
    """
    
    try:
        if message.photo:
            await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text)
        elif message.document:
            await bot.send_document(ADMIN_ID, message.document.file_id, caption=admin_text)
        
        await message.answer("✅ Реквизиты получены! Админ проверит платеж и добавит вас в канал в течение 24 часов.")
        
    except Exception as e:
        logger.error(f"Ошибка отправки админу: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@dp.message(F.text)
async def handle_text(message: types.Message):
    if message.text.startswith('/'):
        return
    
    user_info = f"Пользователь: @{message.from_user.username or 'нет'} ({message.from_user.id})"
    
    admin_text = f"""
🎯 **Новые реквизиты перевода**

{user_info}
📝 **Сообщение:**
{message.text}
    """
    
    try:
        await bot.send_message(ADMIN_ID, admin_text)
        await message.answer("✅ Реквизиты получены! Админ проверит платеж и добавит вас в канал в течение 24 часов.")
    except Exception as e:
        logger.error(f"Ошибка отправки админу: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

async def main():
    logger.info("🚀 Бот запущен на Railway! Работает 24/7")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
