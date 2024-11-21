import asyncio
from aiogram import Bot, Dispatcher

from handlers import user_commands
from callbacks import (
    user_statistic,
    open_main_menu,
    open_admin,
    newsletter,
    add_channel,
    delete_channel,
    admin_stat,
    check_subs,
)

from data.database import initialize_db
from config import TOKEN, DB_PATH


async def main():
    await initialize_db(DB_PATH)

    bot = Bot(TOKEN)
    dp = Dispatcher()

    dp.include_routers(
        user_commands.router,
        user_statistic.router,
        open_main_menu.router,
        open_admin.router,
        newsletter.router,
        add_channel.router,
        delete_channel.router,
        admin_stat.router,
        check_subs.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
