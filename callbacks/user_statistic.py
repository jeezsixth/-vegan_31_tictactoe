import random
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


from data.database import add_user_if_not_exists, get_invite_count
from keyboards.user_inline import get_stat_menu
from config import DB_PATH, BOT_LINK

router = Router()


@router.callback_query(F.data == "get_my_stat")
async def open_main_menu(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()

    user_id = call.from_user.id
    await add_user_if_not_exists(DB_PATH, user_id)
    invites_count = await get_invite_count(DB_PATH, user_id)
    text = f"<b>Ваша ссылка для приглашения друга:</b><code>\n{BOT_LINK}?start={user_id}</code>\n\n<b>Осталось пригласить друзей для получения приза: {5-invites_count}</b>"

    await bot.send_message(
        chat_id=call.message.chat.id,
        text=text,
        parse_mode="html",
        reply_markup=await get_stat_menu(),
        disable_web_page_preview=True,
    )

    await bot.delete_message(call.message.chat.id, call.message.message_id)
