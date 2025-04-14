import asyncio
from contextlib import asynccontextmanager

from steam_client import start_bot


@asynccontextmanager
async def lifespan(app):
    """Фоновый запуск бота при старте сервера"""
    print("🚀 Запускаем фонового бота...")
    bot_task = asyncio.create_task(start_bot())  # Запускаем бота в фоне

    yield  # Ожидание завершения приложения

    print("🛑 Остановка фонового бота...")
    bot_task.cancel()  # Останавливаем бота при завершении сервера
    try:
        await bot_task
    except asyncio.CancelledError:
        pass