import random
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


from data.database import (
    add_user_if_not_exists,
    check_user_exists,
    increment_invite_count,
    get_game_final,
    update_game_final,
    get_invite_count,
)
from data.utils import check_game_result
from keyboards.user_inline import get_main_menu, get_game_keyboard, get_sponsor_sub
from config import (
    DB_PATH,
    get_greeting_message,
    get_need_game_msg,
    lose_message,
    win_message,
    draw_message,
    ADMIN_ID,
)

router = Router()


class GameId(StatesGroup):
    game_id = State()


@router.callback_query(F.data == "check_subs")
async def check_subs(call: CallbackQuery, bot: Bot, state: FSMContext):
    """
    Проверяет значение check_subs_count в данных состояния.
    Если check_subs_count равен 0 или отсутствует, показывает сообщение о необходимости подписки.
    Если значение >= 1, выводит сообщение об успехе.

    :param call: CallbackQuery объект.
    :param bot: Экземпляр бота.
    :param state: Текущее состояние пользователя.
    """
    data = await state.get_data()
    check_subs_count = data.get("check_subs_count", 0)

    if check_subs_count == 0:
        # Уведомление о необходимости подписки
        await call.answer(
            "Вы не подписались ❌\nПодпишитесь и повторите снова", show_alert=True
        )
        # Обновляем значение check_subs_count
        await state.update_data(check_subs_count=check_subs_count + 1)
    else:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        msg_cap = """
Отлично, осталось последнее задание 🔥

Чтобы забрать 360 гемов , пригласи 5 друзей по вашей ссылке , ссылку можно посмотреть нажав кнопку -  статистика 📊
"""

        file = FSInputFile("start_image.jpg")
        await bot.send_photo(
            chat_id=call.message.chat.id,
            photo=file,
            caption=msg_cap,
            parse_mode="html",
            reply_markup=await get_main_menu(),
        )


@router.message(GameId.game_id)
async def game_id(msg: Message, bot: Bot, state: FSMContext):
    user_id = msg.from_user.id
    game_id = msg.text

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Пользователь {user_id} отправил игровой id: {game_id}",
    )

    await msg.answer(text="🎉 Запрос на начисление гемов принят, ожидайте.")
