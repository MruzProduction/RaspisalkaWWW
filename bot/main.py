import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os
from bot.handlers import router
from scheduler.reminder_scheduler import start_scheduler
from data.session import engine
from models.user import User
from models.reminder import Reminder

load_dotenv()

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)

    # Создаём таблицы при первом запуске
    from data.base import Base
    Base.metadata.create_all(bind=engine)

    # Запускаем планировщик
    start_scheduler(bot)

    print("🚀 Raspisalka запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())