"""Проверки аргументов, общие для всех модулей пакета.

Правило одно на весь пакет: аргумент не того типа — ``TypeError``,
аргумент того типа, но с недопустимым значением, — ``ValueError``.
``bool`` числом не считается, хотя в Python ``True`` — это ``int``:
``factorial(True)`` почти наверняка ошибка, а не запрос 1!.
"""
from typing import Any


def check_count(value: Any, name: str) -> None:
    """Проверить, что ``value`` — целое число не меньше нуля.

    >>> check_count(3, "n")
    >>> check_count(-1, "n")
    Traceback (most recent call last):
    ...
    ValueError: n: ожидалось целое число не меньше 0, получено -1
    >>> check_count(True, "n")
    Traceback (most recent call last):
    ...
    TypeError: n: ожидалось целое число, получено True
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name}: ожидалось целое число, получено {value!r}")
    if value < 0:
        raise ValueError(
            f"{name}: ожидалось целое число не меньше 0, получено {value!r}"
        )


def check_callable(value: Any, name: str) -> None:
    """Проверить, что ``value`` можно вызвать как функцию.

    >>> check_callable(abs, "функция")
    >>> check_callable(5, "шаг 2")
    Traceback (most recent call last):
    ...
    TypeError: шаг 2: ожидалась функция, получено 5
    """
    if not callable(value):
        raise TypeError(f"{name}: ожидалась функция, получено {value!r}")
