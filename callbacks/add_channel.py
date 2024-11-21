import random
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


from data.database import add_channel_to_db
from data.utils import check_game_result
from keyboards.admin_inline import get_admin_menu
from keyboards.user_inline import get_stat_menu
from config import (
    DB_PATH,
)

router = Router()


class AddChannel(StatesGroup):
    name = State()
    link = State()


@router.callback_query(F.data == "add_channel")
async def add_channel_start(call: CallbackQuery, bot: Bot, state: FSMContext):
    await bot.send_message(
        chat_id=call.from_user.id,
        text="Введите название канала",
        reply_markup=await get_stat_menu(),
    )

    await state.set_state(AddChannel.name)
    await bot.delete_message(call.message.chat.id, call.message.message_id)


@router.message(AddChannel.name)
async def add_channel_name(msg: Message, state: FSMContext):
    await state.update_data({"name": msg.text})
    await state.set_state(AddChannel.link)
    await msg.reply("Введите ссылку на канал", reply_markup=await get_stat_menu())

    await state.set_state(AddChannel.link)


@router.message(AddChannel.link)
async def add_channel_link(msg: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    name = data.get("name")
    link = msg.text

    await add_channel_to_db(DB_PATH, name, link)

    await bot.send_message(
        chat_id=msg.from_user.id,
        text="Канал успешно добавлен",
        reply_markup=await get_admin_menu(),
    )

    await state.clear()
