#main.py
import os
import sys
import django
import logging
import asyncio
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Добавим путь к Django-проекту (где settings.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'staff_requests'))

# Установка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staff_requests.settings')
django.setup()

load_dotenv()

# Инициализация бота
bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# Импорт обработчиков (после setup Django и путей!)
from bot.handlers.form_handlers import register_handlers, setup as form_handlers_setup
from bot.handlers.callback_handlers import router as callback_router, setup as callback_setup

# Импорт обработчиков
from bot.handlers.form_handlers import register_handlers, setup as form_handlers_setup
from bot.handlers.callback_handlers import router as callback_router, setup as callback_setup

# Загрузка конфигурации
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")
APPROVER_ID = os.getenv("APPROVER_ID")
ALLOWED_ID = os.getenv("ALLOWED_ID")

# Инициализация обработчиков
form_handlers_setup(bot, dp, TARGET_CHAT_ID)
callback_setup(
    bot_instance=bot,
    approver_id=APPROVER_ID,
    allowed_id=ALLOWED_ID
)

# Регистрация роутеров
dp.include_router(callback_router)
register_handlers(dp)

async def main():
    logging.info("Бот запускается...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())