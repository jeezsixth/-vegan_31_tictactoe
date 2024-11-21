import pytz
import aiosqlite
from datetime import datetime, timedelta


async def initialize_db(db_path: str):
    """
    Инициализирует базу данных и создает таблицу users, если она еще не существует.

    :param db_path: Полный путь к БД (например, 'data/database.db').
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    invite_count INTEGER, 
                    invited_by INTEGER,
                    date TEXT,
                    time TEXT,
                    game_final TEXT
                )
            """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS channels (
                    channel_name TEXT,
                    link TEXT
                )
            """
            )
            await db.commit()
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")


async def add_user_if_not_exists(db_path: str, user_id: int, invited_by=0) -> bool:
    """
    Добавляет user_id в таблицу users, если его там нет.
    Возвращает True, если добавление прошло успешно, иначе False.

    :param db_path: Полный путь к БД (например, 'data/database.db').
    :param user_id: Идентификатор пользователя, который нужно добавить.
    :param invited_by: Идентификатор пользователя, пригласившего user_id.
    :return: True, если user_id был добавлен, False, если он уже существует.
    """
    try:
        # Получаем текущую дату и время по Москве
        moscow_tz = pytz.timezone("Europe/Moscow")
        now = datetime.now(moscow_tz)
        current_date = now.strftime("%Y-%m-%d")  # Форматируем дату
        current_time = now.strftime("%H:%M:%S")  # Форматируем время

        async with aiosqlite.connect(db_path) as db:
            async with db.execute(
                "SELECT 1 FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                result = await cursor.fetchone()

            if result is None:
                await db.execute(
                    """
                    INSERT INTO users (user_id, invite_count, invited_by, date, time, game_final) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, 0, invited_by, current_date, current_time, "None"),
                )
                await db.commit()
                return True
            else:
                return False
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")
        return False


async def check_user_exists(db_path: str, user_id: int) -> bool:
    """
    Проверяет, существует ли пользователь с заданным user_id в таблице users.

    :param db_path: Полный путь к БД (например, 'data/database.db').
    :param user_id: Идентификатор пользователя для проверки.
    :return: True, если пользователь существует, иначе False.
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute(
                "SELECT 1 FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                return await cursor.fetchone() is not None
    except Exception as e:
        print(f"Ошибка при проверке существования пользователя: {e}")
        return False


async def increment_invite_count(db_path: str, user_id: int) -> bool:
    """
    Увеличивает значение invite_count на 1 для указанного user_id.

    :param db_path: Полный путь к БД (например, 'data/database.db').
    :param user_id: Идентификатор пользователя, для которого нужно увеличить invite_count.
    :return: True, если операция прошла успешно, иначе False.
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute(
                "UPDATE users SET invite_count = invite_count + 1 WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                if cursor.rowcount == 0:  # Проверяем, была ли затронута строка
                    return False
            await db.commit()
            return True
    except Exception as e:
        print(f"Ошибка при обновлении invite_count: {e}")
        return False


async def get_invite_count(db_path: str, user_id: int) -> int:
    """
    Получает значение invite_count для указанного user_id.

    :param db_path: Полный путь к БД (например, 'data/database.db').
    :param user_id: Идентификатор пользователя, для которого нужно получить invite_count.
    :return: Значение invite_count, или -1, если пользователь не найден.
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute(
                "SELECT invite_count FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else -1
    except Exception as e:
        print(f"Ошибка при получении invite_count: {e}")
        return -1


async def get_user_count(db_path: str) -> int:
    """
    Возвращает количество пользователей в таблице users.

    :param db_path: Полный путь к БД (например, 'data/database.db').
    :return: Количество пользователей в таблице, или -1 в случае ошибки.
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0
    except Exception as e:
        print(f"Ошибка при получении количества пользователей: {e}")
        return -1


async def get_all_user_ids(db_path: str) -> list[int]:
    """
    Возвращает список user_id всех пользователей из таблицы users.

    :param db_path: Полный путь к БД (например, 'data/database.db').
    :return: Список user_id, или пустой список в случае ошибки.
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT user_id FROM users") as cursor:
                return [row[0] for row in await cursor.fetchall()]
    except Exception as e:
        print(f"Ошибка при получении списка user_id: {e}")
        return []


async def get_game_final(db_path: str, user_id: int) -> str | None:
    """
    Возвращает значение поля game_final для указанного user_id.

    :param db_path: Полный путь к базе данных (например, 'data/database.db').
    :param user_id: Идентификатор пользователя, значение game_final которого нужно получить.
    :return: Значение game_final или None, если пользователь не найден.
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute(
                "SELECT game_final FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None
    except Exception as e:
        print(f"Ошибка при получении game_final: {e}")
        return None


async def update_game_final(db_path: str, user_id: int, game_final: str) -> bool:
    """
    Обновляет значение game_final для указанного пользователя в таблице users.

    :param db_path: Полный путь к БД (например, 'data/database.db').
    :param user_id: Идентификатор пользователя.
    :param game_final: Новое значение для поля game_final.
    :return: True, если обновление прошло успешно, иначе False.
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                """
                UPDATE users
                SET game_final = ?
                WHERE user_id = ?
                """,
                (game_final, user_id),
            )
            await db.commit()
            return True
    except Exception as e:
        print(f"Ошибка при обновлении game_final: {e}")
        return False


async def get_channels(db_path: str) -> list[dict[str, str]]:
    """
    Возвращает список каналов из таблицы channels.

    :param db_path: Полный путь к базе данных (например, 'data/database.db').
    :return: Список словарей с данными каналов [{name: "", link: ""}].
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT channel_name, link FROM channels") as cursor:
                rows = await cursor.fetchall()

        # Преобразуем данные в список словарей
        channels = [{"name": row[0], "link": row[1]} for row in rows]
        return channels
    except Exception as e:
        print(f"Ошибка при извлечении каналов: {e}")
        return []


async def add_channel_to_db(db_path: str, channel_name: str, link: str) -> bool:
    """
    Добавляет канал в таблицу channels.

    :param db_path: Полный путь к базе данных (например, 'data/database.db').
    :param channel_name: Название канала.
    :param link: Ссылка на канал.
    :return: True, если добавление прошло успешно, иначе False.
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                """
                INSERT INTO channels (channel_name, link)
                VALUES (?, ?)
                """,
                (channel_name, link),
            )
            await db.commit()
            return True
    except Exception as e:
        print(f"Ошибка при добавлении канала: {e}")
        return False


async def delete_channel(db_path: str, channel_name: str) -> bool:
    """
    Удаляет канал из таблицы channels по его названию.

    :param db_path: Полный путь к базе данных (например, 'data/database.db').
    :param channel_name: Название канала, который нужно удалить.
    :return: True, если удаление прошло успешно, иначе False.
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                """
                DELETE FROM channels
                WHERE channel_name = ?
                """,
                (channel_name,),
            )
            await db.commit()
            return True
    except Exception as e:
        print(f"Ошибка при удалении канала: {e}")
        return False


async def get_registration_stats(db_path: str) -> str:
    """
    Возвращает текстовое сообщение со статистикой регистрации пользователей.

    :param db_path: Полный путь к базе данных (например, 'data/database.db').
    :return: Текстовое сообщение с данными статистики.
    """
    try:
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")  # Текущая дата
        last_hour = (now - timedelta(hours=1)).strftime(
            "%H:%M:%S"
        )  # Время за последний час

        async with aiosqlite.connect(db_path) as db:
            # Пользователи, зарегистрировавшиеся сегодня
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE date = ?", (today,)
            ) as cursor:
                today_total = (await cursor.fetchone())[0]

            # Пользователи, зарегистрировавшиеся сегодня без реферальной ссылки
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE date = ? AND invited_by = 0", (today,)
            ) as cursor:
                today_no_ref = (await cursor.fetchone())[0]

            # Пользователи, зарегистрировавшиеся за последний час
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE date = ? AND time >= ?",
                (today, last_hour),
            ) as cursor:
                last_hour_total = (await cursor.fetchone())[0]

            # Из них с реферальной ссылкой
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE date = ? AND time >= ? AND invited_by != 0",
                (today, last_hour),
            ) as cursor:
                last_hour_with_ref = (await cursor.fetchone())[0]

            # Общее количество пользователей
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                total_users = (await cursor.fetchone())[0]

            # Общее количество пользователей с реферальной ссылкой
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE invited_by != 0"
            ) as cursor:
                total_with_ref = (await cursor.fetchone())[0]

        # Подсчёт значений
        last_hour_no_ref = last_hour_total - last_hour_with_ref
        total_no_ref = total_users - total_with_ref

        # Формирование текста
        message = (
            f"Зарегистрировались сегодня: {today_total}\n"
            f"Без реферальной ссылки: {today_no_ref}\n\n"
            f"За последний час: {last_hour_total}\n"
            f"С реферальной: {last_hour_with_ref}\n"
            f"Без реферальной: {last_hour_no_ref}\n\n"
            f"Всего пользователей: {total_users}\n"
            f"С реферальной: {total_with_ref}\n"
            f"Без реферальной: {total_no_ref}"
        )

        return message

    except Exception as e:
        print(f"Ошибка при создании статистики: {e}")
        return "Ошибка при создании статистики."
