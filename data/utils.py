def check_game_result(moves: dict[int, str | None]) -> bool | None:
    """
    Проверяет результат игры.
    Возвращает True, если победил X,
    False, если победил O,
    None, если игра продолжается или ничья.

    :param moves: Словарь с текущими ходами (1-9).
                  Ключи — позиции (1-9), значения — 'x', 'o' или None.
    :return: True, если X победил; False, если O победил; None, если ничья или игра не окончена.
    """
    # Все выигрышные комбинации
    win_combinations = [
        [1, 2, 3],  # Горизонтальная верхняя линия
        [4, 5, 6],  # Горизонтальная средняя линия
        [7, 8, 9],  # Горизонтальная нижняя линия
        [1, 4, 7],  # Вертикальная левая линия
        [2, 5, 8],  # Вертикальная средняя линия
        [3, 6, 9],  # Вертикальная правая линия
        [1, 5, 9],  # Диагональ слева направо
        [3, 5, 7],  # Диагональ справа налево
    ]

    # Проверяем победу X или O
    for combination in win_combinations:
        if all(moves.get(pos) == "x" for pos in combination):
            return True  # Победил X
        if all(moves.get(pos) == "o" for pos in combination):
            return False  # Победил O

    # Проверяем на ничью
    if all(value in ["x", "o"] for value in moves.values()):
        return "draw"  # Ничья

    # Игра еще продолжается
    return None
