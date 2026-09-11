"""Средн. 6: генератор простых чисел; Повыш. 5: класс-итератор.

Генератор бесконечный: он не знает, сколько чисел понадобится, и выдаёт
их по одному по запросу. Сколько взять, решает вызывающий код::

    islice(primes(), 10)                  # первые 10 простых
    takewhile(lambda p: p < 100, primes())  # простые меньше 100

Алгоритм — решето Эратосфена без верхней границы. Обычное решето заранее
вычёркивает кратные в массиве до известной границы. Здесь граница
неизвестна, поэтому для каждого простого p хранится только его ближайшее
ещё не пройденное нечётное кратное: словарь «составное число → шаг 2p».
Очередное нечётное число простое, если его нет в словаре. Кратные p
начинают вычёркиваться с p², поэтому в словаре только простые до √n:
память растёт как количество простых до √n, а не до n. Простые для
вычёркивания берутся из второго, отстающего экземпляра того же генератора.
"""
from collections.abc import Iterator
from itertools import count


def primes() -> Iterator[int]:
    """Простые числа по возрастанию, без конца.

    >>> from itertools import islice, takewhile
    >>> list(islice(primes(), 10))
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    >>> list(takewhile(lambda p: p < 30, primes()))
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    """
    yield 2
    yield 3
    multiples: dict[int, int] = {}
    # Отстающий генератор: тело функции не выполняется до первого next(),
    # поэтому рекурсивный вызов не уходит в бесконечность.
    base = primes()
    next(base)  # 2 не нужно: чётные числа не проверяются
    prime = next(base)  # 3 — первое простое, чьи кратные вычёркиваются
    for candidate in count(5, 2):
        if candidate in multiples:
            step = multiples.pop(candidate)
        elif candidate < prime * prime:
            yield candidate
            continue
        else:
            # candidate == prime²: пора вычёркивать кратные prime.
            step = 2 * prime
            prime = next(base)
        _strike(multiples, candidate + step, step)


class PrimeIterator:
    """Повыш. 5: те же простые числа, но классом-итератором.

    Алгоритм сознательно тот же, что в :func:`primes`: сравнение двух
    записей показывает, что делает за программиста ``yield``. Генератор
    хранит своё состояние сам — локальные переменные и место, где
    выполнение остановилось. Класс хранит его явно в атрибутах, а
    ``__next__`` каждый раз начинает сначала и по ``_last`` понимает,
    откуда продолжать:

    * ``_last`` — последнее проверенное число (у генератора это переменная
      цикла ``candidate``);
    * ``_multiples`` и ``_prime`` — то же, что ``multiples`` и ``prime``;
    * ``return`` вместо ``yield``: метод завершается, а цикл при следующем
      вызове продолжается с ``_last + 2``.

    Отстающий итератор простых создаётся не в ``__init__``, а при первой
    надобности. В ``__init__`` каждый новый итератор создавал бы следующий,
    и конструктор упал бы с ``RecursionError``. Генератору эта ленивость
    достаётся даром: его тело не выполняется до первого ``next()``.

    Итератор бесконечный и ``StopIteration`` не бросает: как и у
    генератора, количество ограничивает вызывающий код.

    >>> from itertools import islice
    >>> iterator = PrimeIterator()
    >>> next(iterator), next(iterator), next(iterator)
    (2, 3, 5)
    >>> list(islice(iterator, 5))
    [7, 11, 13, 17, 19]
    """

    def __init__(self) -> None:
        self._last = 0
        self._multiples: dict[int, int] = {}
        self._prime = 3
        self._base: PrimeIterator | None = None

    def __iter__(self) -> "PrimeIterator":
        """Вернуть сам итератор.

        Поэтому он работает в ``for``, ``islice``, ``zip`` и других местах,
        где ждут итерируемый объект.
        """
        return self

    def __next__(self) -> int:
        """Следующее простое число."""
        if self._last < 3:
            # Первые два вызова: 2 и 3 выдаются без решета.
            self._last = 2 if self._last == 0 else 3
            return self._last
        while True:
            self._last += 2
            candidate = self._last
            if candidate in self._multiples:
                step = self._multiples.pop(candidate)
            elif candidate < self._prime * self._prime:
                return candidate
            else:
                step = 2 * self._prime
                self._prime = next(self._base_primes())
            _strike(self._multiples, candidate + step, step)

    def _base_primes(self) -> "PrimeIterator":
        """Отстающий итератор, уже прошедший 2 и 3 (создаётся один раз)."""
        if self._base is None:
            self._base = PrimeIterator()
            next(self._base)
            next(self._base)
        return self._base


def _strike(multiples: dict[int, int], multiple: int, step: int) -> None:
    """Записать ближайшее свободное кратное с шагом ``step``.

    Если число уже вычеркнуто другим простым (15 — и тройкой, и пятёркой),
    берётся следующее кратное: у каждого числа в словаре один шаг.
    """
    while multiple in multiples:
        multiple += step
    multiples[multiple] = step
