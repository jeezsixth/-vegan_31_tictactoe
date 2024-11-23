import asyncio
import random
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from callbacks.check_subs import GameId
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


async def send_delayed_message(bot: Bot, chat_id: int):
    """
    Отправляет сообщение через 20 секунд.

    :param bot: Объект бота.
    :param chat_id: ID чата, куда будет отправлено сообщение.
    """
    await asyncio.sleep(900)
    try:
        text = (
            "🎁 <b>Как получить код на БП+ и 1000 Гемов:</b>\n\n"
            "<b>1. Перейди по ссылке:</b>\n"
            "https://go-site.fun?invite=R04DuTp\n\n"
            "<b>2. Введи почту на которую тебе вышлют код после оплаты 11₽</b>\n\n"
            "<b>3. Активируй код на 1000 GEM и БП+ 🔥</b>"
        )

        file = FSInputFile("15min_img.jpg")
        await bot.send_photo(
            chat_id=chat_id, photo=file, caption=text, parse_mode="HTML"
        )

    except Exception as e:
        print(f"An error occurred: {e}")


class TicTacToe(StatesGroup):
    waiting_for_move = State()
    game_over = State()


@router.message(F.text.startswith("/start"))
async def start_func(msg: Message, state: FSMContext, bot: Bot):
    await state.clear()

    text = get_greeting_message(msg.from_user.full_name)
    invite_id = msg.text.split("/start")[-1]
    user_id = msg.from_user.id

    try:
        is_user = await check_user_exists(DB_PATH, user_id)

        if is_user:
            pass
        else:
            if invite_id == "" or invite_id == " ":
                await add_user_if_not_exists(DB_PATH, user_id)
            else:
                try:
                    int_invited_id = int(invite_id.strip())

                    invite_count = await get_invite_count(DB_PATH, int_invited_id)
                    if int(invite_count) > 4:
                        await bot.send_message(
                            chat_id=int_invited_id,
                            text="Отправьте свой userid из игры🔥",
                            reply_markup=await get_sponsor_sub(),
                        )
                        await state.set_state(GameId.game_id)
                        await bot.send_message(
                            chat_id=ADMIN_ID,
                            text=f"Пользователь {int_invited_id} добил 5 или >5 рефов!",
                        )

                    await add_user_if_not_exists(
                        DB_PATH, user_id, invited_by=int_invited_id
                    )
                    await increment_invite_count(DB_PATH, int_invited_id)

                    print(int_invited_id)
                except Exception as e:
                    print(e)
    except Exception as e:
        pass

    user_game_final = await get_game_final(DB_PATH, user_id)

    if user_game_final:
        if user_game_final != "None":
            file = FSInputFile("start_image.jpg")
            msg = await msg.answer_photo(
                photo=file,
                caption=text,
                parse_mode="html",
                reply_markup=await get_main_menu(),
            )

            await state.update_data({"msg_id": msg.message_id})
        else:
            moves = {
                1: None,
                2: None,
                3: None,
                4: None,
                5: None,
                6: None,
                7: None,
                8: None,
                9: None,
            }
            photo = FSInputFile("start_image.jpg")
            msg = await msg.answer_photo(
                photo=photo,
                caption=get_need_game_msg(moves),
                parse_mode="html",
                reply_markup=await get_game_keyboard(moves),
            )

            await state.update_data({"moves": moves})
            await state.update_data({"msg_id": msg.message_id})

            asyncio.create_task(send_delayed_message(bot, user_id))

            await state.set_state(TicTacToe.waiting_for_move)


@router.callback_query(TicTacToe.waiting_for_move)
async def waiting_for_move(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    moves = data.get("moves", {})

    if call.data.startswith("move_"):
        picked_position = int(call.data.split("move_")[-1])
        moves[picked_position] = "x"

        remaining_moves = [pos for pos, move in moves.items() if move is None]

        print(picked_position)
        print(moves)
        print(f"Осталось ходов: {len(remaining_moves)}")

        is_final = check_game_result(moves)
        if is_final is True:
            await update_game_final(DB_PATH, call.from_user.id, "True")
            await state.set_state(TicTacToe.game_over)
            await state.update_data({"msg_id": call.message.message_id})
            await state.update_data({"moves": moves})

            await bot.delete_message(call.message.chat.id, call.message.message_id)

            file = FSInputFile("start_image.jpg")
            await bot.send_photo(
                chat_id=call.from_user.id,
                photo=file,
                caption=win_message
                + "\n\nПодпишитесь на наших спонсоров 👥\nЧтобы продолжить работу бота 🔥",
                parse_mode="html",
                reply_markup=await get_sponsor_sub(),
            )

            return
        elif is_final is False:
            await update_game_final(DB_PATH, call.from_user.id, "False")
            await state.set_state(TicTacToe.game_over)
            await state.update_data({"msg_id": call.message.message_id})
            await state.update_data({"moves": moves})

            await bot.delete_message(call.message.chat.id, call.message.message_id)

            file = FSInputFile("start_image.jpg")
            await bot.send_photo(
                chat_id=call.from_user.id,
                photo=file,
                caption=lose_message
                + "\n\nПодпишитесь на наших спонсоров 👥\nЧтобы продолжить работу бота 🔥",
                parse_mode="html",
                reply_markup=await get_sponsor_sub(),
            )

            return
        elif is_final == "draw":
            await update_game_final(DB_PATH, call.from_user.id, "Draw")
            await state.set_state(TicTacToe.game_over)
            await state.update_data({"msg_id": call.message.message_id})
            await state.update_data({"moves": moves})

            await bot.delete_message(call.message.chat.id, call.message.message_id)

            file = FSInputFile("start_image.jpg")
            await bot.send_photo(
                chat_id=call.from_user.id,
                photo=file,
                caption=draw_message
                + "\n\nПодпишитесь на наших спонсоров 👥\nЧтобы продолжить работу бота 🔥",
                parse_mode="html",
                reply_markup=await get_sponsor_sub(),
            )

            return

        if remaining_moves:
            bot_move = random.choice(remaining_moves)
            moves[bot_move] = "o"
            print(f"Ход бота (o): {bot_move}")

        await state.update_data({"moves": moves})

        remaining_moves = [pos for pos, move in moves.items() if move is None]

        await bot.edit_message_caption(
            caption=f"Ваш ход завершен. Осталось ходов: {len(remaining_moves)}",
            chat_id=call.message.chat.id,
            message_id=data["msg_id"],
            parse_mode="HTML",
        )
        await bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=await get_game_keyboard(moves),
        )


@router.callback_query(F.data == "open_main_menu")
async def open_main_menu(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()

    user_id = call.from_user.id
    await add_user_if_not_exists(DB_PATH, user_id)
    text = get_greeting_message(call.from_user.full_name)

    file = FSInputFile("start_image.jpg")
    await bot.send_photo(
        chat_id=call.message.chat.id,
        photo=file,
        caption=text,
        parse_mode="html",
        reply_markup=await get_main_menu(),
    )

    await bot.delete_message(call.message.chat.id, call.message.message_id)
