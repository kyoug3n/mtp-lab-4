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
вычёркивания берутся из отстающего экземпляра той же реализации; он, в
свою очередь, заводит свой, но цепочка короткая: её глубина растёт как
log log n (для первых 100 000 простых — четыре уровня).

Сам алгоритм записан один раз — в :class:`_Sieve`. Обе реализации
отличаются только тем, как хранят состояние обхода: генератор — за счёт
``yield``, класс — в явных атрибутах. Ради этого сравнения задание
Повыш. 5 и существует, поэтому повторять ещё и арифметику решета незачем.
"""
from collections.abc import Callable, Iterator
from itertools import count

# Двойка и тройка выдаются без решета: чётные числа не проверяются, а
# вычёркивание кратных начинается только с 3² = 9.
FIRST_PRIMES = (2, 3)


class _Sieve:
    """Решето без верхней границы: общее ядро генератора и итератора.

    Хранит словарь «составное → шаг», текущее простое, кратные которого
    ещё не начали вычёркиваться, и отстающий источник простых. Обход
    чисел решето не ведёт: числа ему приносят снаружи по одному.
    """

    def __init__(self, source: Callable[[], Iterator[int]]) -> None:
        self._source = source
        self._base: Iterator[int] | None = None
        self._multiples: dict[int, int] = {}
        self._prime = FIRST_PRIMES[-1]

    def __len__(self) -> int:
        """Сколько чисел вычеркнуто наперёд — по одному на простое до √n."""
        return len(self._multiples)

    def accepts(self, candidate: int) -> bool:
        """Простое ли нечётное ``candidate`` (больше 3).

        Попутно поддерживает решето: вычеркнутое число заменяется
        следующим кратным того же простого, а если дошли до p² — начинают
        вычёркиваться кратные p и берётся следующее простое.
        """
        if candidate in self._multiples:
            step = self._multiples.pop(candidate)
        elif candidate < self._prime * self._prime:
            return True
        else:
            # candidate == prime²: пора вычёркивать кратные prime.
            step = 2 * self._prime
            self._prime = next(self._base_primes())
        self._strike(candidate + step, step)
        return False

    def _base_primes(self) -> Iterator[int]:
        """Отстающий источник простых, уже прошедший 2 и 3.

        Создаётся при первой надобности, а не в ``__init__``: иначе каждое
        решето создавало бы следующее и конструктор упал бы с
        ``RecursionError``.
        """
        if self._base is None:
            self._base = self._source()
            for _ in FIRST_PRIMES:
                next(self._base)
        return self._base

    def _strike(self, multiple: int, step: int) -> None:
        """Записать ближайшее свободное кратное с шагом ``step``.

        Если число уже вычеркнуто другим простым (15 — и тройкой, и
        пятёркой), берётся следующее кратное: у каждого числа один шаг.
        """
        while multiple in self._multiples:
            multiple += step
        self._multiples[multiple] = step


def primes() -> Iterator[int]:
    """Простые числа по возрастанию, без конца.

    >>> from itertools import islice, takewhile
    >>> list(islice(primes(), 10))
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    >>> list(takewhile(lambda p: p < 30, primes()))
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    """
    yield from FIRST_PRIMES
    # Тело генератора не выполняется до первого next(), поэтому решето
    # может брать простые из такого же генератора без бесконечной рекурсии.
    sieve = _Sieve(primes)
    for candidate in count(5, 2):
        if sieve.accepts(candidate):
            yield candidate


class PrimeIterator:
    """Повыш. 5: те же простые числа, но классом-итератором.

    Решето у класса то же самое (:class:`_Sieve`), и это делает сравнение
    честным: видно ровно то, что делает за программиста ``yield``.
    Генератор хранит состояние обхода сам — локальные переменные и место,
    где выполнение остановилось. Класс хранит его явно в атрибутах, а
    ``__next__`` каждый раз начинает сначала и по ним понимает, откуда
    продолжать:

    * ``_emitted`` — сколько чисел из ``FIRST_PRIMES`` уже выдано (у
      генератора это место остановки на ``yield from``);
    * ``_last`` — последнее проверенное число (у генератора это переменная
      цикла ``candidate``);
    * ``return`` вместо ``yield``: метод завершается, а цикл при следующем
      вызове продолжается с ``_last + 2``.

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
        self._emitted = 0
        self._last = FIRST_PRIMES[-1]
        self._sieve = _Sieve(PrimeIterator)

    def __iter__(self) -> "PrimeIterator":
        """Вернуть сам итератор.

        Поэтому он работает в ``for``, ``islice``, ``zip`` и других местах,
        где ждут итерируемый объект.
        """
        return self

    def __next__(self) -> int:
        """Следующее простое число."""
        if self._emitted < len(FIRST_PRIMES):
            prime = FIRST_PRIMES[self._emitted]
            self._emitted += 1
            return prime
        while True:
            self._last += 2
            if self._sieve.accepts(self._last):
                return self._last

    def __copy__(self) -> "PrimeIterator":
        """Запретить поверхностное копирование.

        ``copy.copy`` скопировал бы ссылку на решето, и две «независимые»
        копии портили бы состояние друг друга, молча выдавая составные
        числа. Генераторы Python по той же причине не копируются вовсе.
        ``copy.deepcopy`` работает: он копирует и состояние.
        """
        raise TypeError(
            "PrimeIterator нельзя копировать поверхностно: копия делила бы "
            "состояние решета (для копии используйте copy.deepcopy)"
        )
