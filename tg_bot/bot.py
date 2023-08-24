import asyncio
from distutils.cmd import Command

from aiogram import Bot, Dispatcher

from configs import configure_logging, config
from handlers import questions, different_types


async def main():
    bot = Bot(token=config.tg_bot_token.get_secret_value())
    dp = Dispatcher()

    dp.include_routers(questions.router, different_types.router)

    # Альтернативный вариант регистрации роутеров по одному на строку
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    configure_logging("tg_bot.log")

    asyncio.run(main())
