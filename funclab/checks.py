"""Проверки аргументов, общие для всех модулей пакета.

Правило одно на весь пакет: аргумент не того типа — ``TypeError``,
аргумент того типа, но с недопустимым значением, — ``ValueError``.
``bool`` числом не считается, хотя в Python ``True`` — это ``int``:
``factorial(True)`` почти наверняка ошибка, а не запрос 1!.

Сообщение всегда начинается с имени аргумента, чтобы из любого модуля
ошибки выглядели одинаково: «n: …», «функция 2: …», «шаг 3: …».
"""
from collections.abc import Iterable, Iterator
from typing import Any


def check_non_negative_int(
    value: Any, name: str, maximum: int | None = None
) -> None:
    """Проверить, что ``value`` — целое от нуля до ``maximum``.

    >>> check_non_negative_int(3, "n")
    >>> check_non_negative_int(-1, "n")
    Traceback (most recent call last):
    ...
    ValueError: n: ожидалось целое число не меньше 0, получено -1
    >>> check_non_negative_int(True, "n")
    Traceback (most recent call last):
    ...
    TypeError: n: ожидалось целое число, получено True
    >>> check_non_negative_int(10, "сколько", maximum=9)
    Traceback (most recent call last):
    ...
    ValueError: сколько: ожидалось целое число не больше 9, получено 10
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name}: ожидалось целое число, получено {value!r}")
    if value < 0:
        raise ValueError(
            f"{name}: ожидалось целое число не меньше 0, получено {value!r}"
        )
    if maximum is not None and value > maximum:
        raise ValueError(
            f"{name}: ожидалось целое число не больше {maximum}, "
            f"получено {value!r}"
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


def check_callables(values: Iterable[Any], name: str) -> None:
    """Проверить набор функций, нумеруя их с единицы в сообщении.

    >>> check_callables([abs, 5], "функция")
    Traceback (most recent call last):
    ...
    TypeError: функция 2: ожидалась функция, получено 5
    """
    for position, value in enumerate(values, start=1):
        check_callable(value, f"{name} {position}")


def as_stream(value: Any, name: str) -> Iterator[Any]:
    """Итератор по ``value`` с понятной ошибкой, если это не поток.

    >>> as_stream(42, "данные")
    Traceback (most recent call last):
    ...
    TypeError: данные: ожидался итерируемый объект, получено 42

    Исходная ошибка остаётся причиной (``__cause__``): если ``__iter__``
    самого объекта упал с ``TypeError``, это будет видно в трассировке.
    """
    try:
        return iter(value)
    except TypeError as error:
        raise TypeError(
            f"{name}: ожидался итерируемый объект, получено {value!r}"
        ) from error
