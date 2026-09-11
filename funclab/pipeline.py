"""Повыш. 9: конвейер (pipeline) обработки данных.

Шаг конвейера — функция «поток → поток»: принимает итерируемый объект и
возвращает новый. :func:`pipeline` соединяет шаги в одну функцию, которая
пропускает данные через них по порядку, слева направо. Соединяет их
``reduce``: поток сворачивается по списку шагов — по сути
``reduce(lambda stream, step: step(stream), steps, data)``.

Готовые шаги — обёртки над ленивыми встроенными средствами:
:func:`keep` над ``filter``, :func:`transform` над ``map``, :func:`take`
над ``itertools.islice``. Промежуточных списков нет: каждый элемент
проходит все шаги, прежде чем конвейер возьмёт следующий, а ``take``
перестаёт запрашивать элементы, как только набрал нужное число. Поэтому на
вход можно подать и бесконечный поток — например,
:func:`funclab.primes.primes`.

Шагом может быть любая функция «итерируемое → итерируемое», в том числе
``sorted`` или другой конвейер. Ограничение: шаг вроде ``sorted`` читает
весь поток сразу, как только конвейер запущен, и на бесконечном входе не
завершится.
"""
from collections.abc import Callable, Iterable, Iterator
import sys
from functools import reduce
from itertools import islice
from typing import Any, TypeVar

from funclab.checks import (
    as_stream,
    check_callable,
    check_callables,
    check_non_negative_int,
)

T = TypeVar("T")
R = TypeVar("R")

Step = Callable[[Iterable[Any]], Iterable[Any]]


def pipeline(*steps: Step) -> Callable[[Iterable[Any]], Iterator[Any]]:
    """Соединить шаги в конвейер.

    Шаги проверяются сразу, при сборке, а не при первом запуске.
    Собранный конвейер можно запускать сколько угодно раз: каждый запуск
    создаёт свою цепочку ленивых итераторов. Конвейер без шагов выдаёт те
    же элементы, что были на входе.

    >>> from funclab.primes import primes
    >>> pick = pipeline(
    ...     keep(lambda p: p % 4 == 1),
    ...     transform(lambda p: p * 10),
    ...     take(5),
    ... )
    >>> list(pick(primes()))
    [50, 130, 170, 290, 370]
    >>> list(pick([1, 5, 9, 2]))
    [10, 50, 90]

    Номер шага попадает в сообщение об ошибке — и при сборке, и когда шаг
    вернул не поток. Ошибка внутри самой функции пользователя приходит от
    неё без номера, как если бы её вызвали напрямую.

    :raises TypeError: при сборке — если шаг не функция; при запуске —
        если данные или результат шага не итерируемые.
    """
    check_callables(steps, "шаг")

    def run(data: Iterable[Any]) -> Iterator[Any]:
        return reduce(
            _apply_step,
            enumerate(steps, start=1),
            as_stream(data, "данные"),
        )

    return run


def keep(
    predicate: Callable[[T], object]
) -> Callable[[Iterable[T]], Iterator[T]]:
    """Шаг: оставить элементы, для которых ``predicate`` истинно.

    :raises TypeError: если ``predicate`` не функция.
    """
    check_callable(predicate, "условие")
    return lambda stream: filter(predicate, stream)


def transform(
    function: Callable[[T], R]
) -> Callable[[Iterable[T]], Iterator[R]]:
    """Шаг: заменить каждый элемент ``x`` на ``function(x)``.

    :raises TypeError: если ``function`` не функция.
    """
    check_callable(function, "преобразование")
    return lambda stream: map(function, stream)


def take(count: int) -> Callable[[Iterable[T]], Iterator[T]]:
    """Шаг: первые ``count`` элементов; остальные даже не запрашиваются.

    Верхняя граница ``sys.maxsize`` — ограничение ``islice``; без проверки
    ``take(10**100)`` собрался бы, а упал только при запуске, да ещё
    сообщением на английском.

    :raises TypeError: если ``count`` не целое число.
    :raises ValueError: если ``count`` отрицательное или больше
        ``sys.maxsize``.
    """
    check_non_negative_int(count, "сколько", maximum=sys.maxsize)
    return lambda stream: islice(stream, count)


def _apply_step(
    stream: Iterator[Any], numbered: tuple[int, Step]
) -> Iterator[Any]:
    """Один шаг свёртки: пропустить поток через шаг с номером."""
    position, step = numbered
    return as_stream(step(stream), f"шаг {position}")
