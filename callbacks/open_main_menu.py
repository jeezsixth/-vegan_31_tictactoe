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
)
from data.utils import check_game_result
from keyboards.user_inline import get_main_menu, get_game_keyboard
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


@router.callback_query(F.data == "open_main_menu")
async def open_main_menu(call: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = call.from_user.id
    await add_user_if_not_exists(DB_PATH, user_id)
    text = get_greeting_message(call.from_user.full_name)

    if user_id == ADMIN_ID:
        await state.clear()

    file = FSInputFile("start_image.jpg")
    await bot.send_photo(
        chat_id=call.message.chat.id,
        photo=file,
        caption=text,
        parse_mode="html",
        reply_markup=await get_main_menu(),
    )

    await bot.delete_message(call.message.chat.id, call.message.message_id)
