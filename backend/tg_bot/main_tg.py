import asyncio
from aiogram import Bot, Dispatcher
from bot import dp, bot
import config

async def main():
    """Запуск бота"""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
# установите pip install aiogram passlib sqlalchemy asyncio python-dotenv
# запуск python main.py, мб python3 main.py