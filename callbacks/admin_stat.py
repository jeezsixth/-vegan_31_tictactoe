import random
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from data.database import get_registration_stats
from keyboards.admin_inline import get_admin_menu
from config import DB_PATH, BOT_LINK, ADMIN_ID

router = Router()


@router.callback_query(F.data == "get_admin_stat")
async def open_admin_stat(call: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = call.from_user.id

    if user_id == ADMIN_ID:
        msg_text = await get_registration_stats(DB_PATH)

        await bot.send_message(
            chat_id=ADMIN_ID,
            text=msg_text,
            reply_markup=await get_admin_menu(),
        )
        await bot.delete_message(call.message.chat.id, call.message.message_id)
