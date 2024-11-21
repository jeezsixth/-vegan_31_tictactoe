import random
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


from data.database import delete_channel
from keyboards.admin_inline import get_admin_menu
from keyboards.user_inline import get_stat_menu
from config import (
    DB_PATH,
)

router = Router()


class DeleteChannel(StatesGroup):
    name = State()


@router.callback_query(F.data == "del_channel")
async def delete_channel_start(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(DeleteChannel.name)
    await bot.send_message(
        chat_id=call.from_user.id,
        text="Введите название канала, который нужно удалить",
        reply_markup=await get_stat_menu(),
    )

    await bot.delete_message(call.message.chat.id, call.message.message_id)


@router.message(DeleteChannel.name)
async def delete_channel_end(msg: Message, bot: Bot, state: FSMContext):
    channel_name = msg.text
    await delete_channel(DB_PATH, channel_name)
    await bot.send_message(
        chat_id=msg.from_user.id,
        text="Канал успешно удален",
        reply_markup=await get_admin_menu(),
    )

    await state.clear()
