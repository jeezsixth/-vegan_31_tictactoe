import os

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards.admin_inline import get_admin_menu
from keyboards.user_inline import get_stat_menu
from data.database import get_all_user_ids
from config import DB_PATH, ADMIN_ID

router = Router()


class Newsletter(StatesGroup):
    text = State()
    image = State()


@router.callback_query(F.data == "newsletter")
async def newsletter_func(call: CallbackQuery, bot: Bot, state: FSMContext):
    if call.from_user.id == ADMIN_ID:
        await state.set_state(Newsletter.text)
        await bot.send_message(
            chat_id=ADMIN_ID,
            text="Отправьте текст рассылки",
            reply_markup=await get_stat_menu(),
        )
    else:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text="Вы не администратор",
            reply_markup=await get_admin_menu(),
        )

    await bot.delete_message(call.message.chat.id, call.message.message_id)

    await state.set_state(Newsletter.text)


@router.message(Newsletter.text)
async def newsletter_text_func(msg: Message, state: FSMContext):
    await state.update_data(text=msg.text)
    await state.set_state(Newsletter.image)
    await msg.reply("Отправьте изображение", reply_markup=await get_stat_menu())

    await state.set_state(Newsletter.image)


@router.message(Newsletter.image)
async def newsletter_image_func(msg: Message, state: FSMContext, bot: Bot):
    await state.set_state(Newsletter.text)

    data = await state.get_data()
    text = data.get("text")

    file_id = msg.photo[-1].file_id
    file_name = "image.jpg"  # Укажите путь для сохранения
    await bot.download(file_id, file_name)

    user_ids = await get_all_user_ids(DB_PATH)

    error = 0
    success = 0
    for user_id in user_ids:
        try:
            await bot.send_photo(
                chat_id=user_id,
                photo=FSInputFile(file_name),
                caption=text,
                parse_mode="html",
                reply_markup=await get_stat_menu(),
            )
            success += 1
        except:
            error += 1

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Рассылка завершена\n\nУспешно отправлено: {success}\nНе удалось отправить: {error}",
        parse_mode="html",
        reply_markup=await get_admin_menu(),
    )

    try:
        os.remove(file_name)
    except:
        pass

    await state.clear()
