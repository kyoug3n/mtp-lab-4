"""Средн. 6: генератор простых чисел.

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


def _strike(multiples: dict[int, int], multiple: int, step: int) -> None:
    """Записать ближайшее свободное кратное с шагом ``step``.

    Если число уже вычеркнуто другим простым (15 — и тройкой, и пятёркой),
    берётся следующее кратное: у каждого числа в словаре один шаг.
    """
    while multiple in multiples:
        multiple += step
    multiples[multiple] = step
