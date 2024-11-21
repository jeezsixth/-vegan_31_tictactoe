from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_admin_menu():
    kb = [
        [InlineKeyboardButton(text="＋ Добавить канал", callback_data="add_channel")],
        [InlineKeyboardButton(text="－ Удалить канал", callback_data="del_channel")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="get_admin_stat")],
        [InlineKeyboardButton(text="📝 Рассылка", callback_data="newsletter")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard
