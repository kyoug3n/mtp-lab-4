"""Тесты генератора простых чисел и решета (Средн. 6)."""
import inspect
import unittest
from collections import deque
from itertools import count, islice, takewhile
from math import isqrt

from funclab.primes import FIRST_PRIMES, PrimeIterator, _Sieve, primes


def is_prime(number: int) -> bool:
    """Наивная проверка делением — независимый эталон для сверки."""
    return number >= 2 and all(
        number % divisor for divisor in range(2, isqrt(number) + 1)
    )


def run_sieve(amount: int) -> tuple[_Sieve, int]:
    """Прогнать решето до ``amount``-го простого; вернуть его и число."""
    sieve = _Sieve(primes)
    found = len(FIRST_PRIMES)
    for candidate in count(5, 2):
        if sieve.accepts(candidate):
            found += 1
            if found == amount:
                return sieve, candidate
    raise AssertionError("недостижимо: count бесконечен")


class PrimesTests(unittest.TestCase):
    def test_matches_naive_check_up_to_20000(self) -> None:
        expected = [n for n in range(20000) if is_prime(n)]
        got = list(takewhile(lambda p: p < 20000, primes()))
        self.assertEqual(got, expected)

    def test_known_nth_primes(self) -> None:
        # 1000-е и 10000-е простые числа — известные значения.
        for position, value in ((1000, 7919), (10000, 104729)):
            with self.subTest(position=position):
                self.assertEqual(next(islice(primes(), position - 1, None)),
                                 value)

    def test_is_a_generator(self) -> None:
        self.assertTrue(inspect.isgeneratorfunction(primes))

    def test_values_are_computed_on_demand(self) -> None:
        # Генератор бесконечен: если бы он считал всё заранее, этот вызов
        # не вернулся бы.
        self.assertEqual(list(islice(primes(), 3)), [2, 3, 5])

    def test_generators_are_independent(self) -> None:
        first, second = primes(), primes()
        self.assertEqual([next(first) for _ in range(5)], [2, 3, 5, 7, 11])
        self.assertEqual(next(second), 2)
        self.assertEqual(next(first), 13)


class SieveTests(unittest.TestCase):
    """Решето — общее ядро генератора и класса-итератора."""

    def test_keeps_one_entry_per_odd_prime_up_to_root(self) -> None:
        # Отсюда и берётся экономия памяти: хранятся не найденные простые,
        # а только те, чей квадрат уже пройден, — то есть простые до √n.
        # Сравнение точное, без измерения памяти и порогов.
        for amount in (1_000, 10_000, 100_000):
            with self.subTest(amount=amount):
                sieve, last = run_sieve(amount)
                expected = sum(1 for odd in range(3, isqrt(last) + 1, 2)
                               if is_prime(odd))
                self.assertEqual(len(sieve), expected)
                # Найденных простых на порядок больше, чем хранимых,
                # и с ростом amount разрыв только увеличивается.
                self.assertLess(len(sieve) * 10, amount)

    def test_chain_of_lagging_sieves_is_short(self) -> None:
        # Каждому решету нужны простые до √n, тому — до √√n и так далее,
        # поэтому цепочка растёт как log log n. Считаются все решёта
        # вместе с основным.
        iterator = PrimeIterator()
        deque(islice(iterator, 100_000), maxlen=0)
        sieve, levels = iterator._sieve, 1
        while sieve._base is not None:
            base = sieve._base
            assert isinstance(base, PrimeIterator)
            sieve, levels = base._sieve, levels + 1
        self.assertEqual(levels, 4)


if __name__ == "__main__":
    unittest.main()
