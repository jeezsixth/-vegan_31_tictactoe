from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import REVIEWS_LINK, DB_PATH
from data.database import get_channels


async def get_main_menu():
    kb = [
        [InlineKeyboardButton(text="📊 Статистика", callback_data="get_my_stat")],
        [InlineKeyboardButton(text="💭 Отзывы", url=REVIEWS_LINK)],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard


async def get_stat_menu():
    kb = [
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="open_main_menu")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard


async def get_game_keyboard(moves: dict[int, str | None]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для отображения текущей таблицы игры и управления ходами.

    :param moves: Словарь с позициями и ходами (например, {1: 'x', 2: 'o', 3: None}).
                  Ключи — номера позиций (1-9), значения — 'x', 'o' или None.
    :return: InlineKeyboardMarkup с текущей таблицей игры.
    """
    # Символы для отображения
    symbols = {"x": "❌", "o": "⭕️", None: "⬜️"}  # Пустая клетка

    kb = []

    # Формируем клавиатуру строками (3x3)
    for row in range(0, 9, 3):
        row_buttons = []
        for position in range(row + 1, row + 4):
            move = moves.get(position, None)
            if move is None:
                # Кнопка для хода пользователя
                button = InlineKeyboardButton(
                    text=symbols[None], callback_data=f"move_{position}"
                )
            else:
                # Кнопка с заблокированным ходом
                button = InlineKeyboardButton(
                    text=symbols[move.lower()], callback_data="nothing"
                )
            row_buttons.append(button)
        kb.append(row_buttons)

    return InlineKeyboardMarkup(inline_keyboard=kb)


async def get_sponsor_sub():
    channels = await get_channels(DB_PATH)
    kb = [
        [InlineKeyboardButton(text=channel["name"], url=channel["link"])]
        for channel in channels
    ]

    kb.append([InlineKeyboardButton(text="Проверить ✅", callback_data="check_subs")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard
