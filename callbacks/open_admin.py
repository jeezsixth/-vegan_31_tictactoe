import random
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


from data.database import get_channels
from keyboards.admin_inline import get_admin_menu
from config import DB_PATH, BOT_LINK, ADMIN_ID

router = Router()


@router.message(F.text == "/admin")
async def open_admin_menu(msg: Message, bot: Bot, state: FSMContext):
    user_id = msg.from_user.id
    channels = await get_channels(DB_PATH)
    msg_text = f"Список каналов:\n\n"
    for channel in channels:
        msg_text += f"{channel['name']}\n{channel['link']}\n\n"

    if user_id == ADMIN_ID:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=msg_text + "\nВы вошли в админ панель",
            reply_markup=await get_admin_menu(),
        )
        await bot.delete_message(msg.chat.id, msg.message_id)
    else:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text="Вы не администратор",
            reply_markup=await get_admin_menu(),
        )
