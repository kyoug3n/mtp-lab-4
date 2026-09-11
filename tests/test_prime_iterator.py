"""Тесты класса-итератора простых чисел (Повыш. 5)."""
import tracemalloc
import unittest
from collections import deque
from collections.abc import Iterator
from itertools import islice

from funclab.primes import PrimeIterator, primes


class PrimeIteratorTests(unittest.TestCase):
    def test_same_numbers_as_generator(self) -> None:
        # Две записи одного алгоритма: класс и генератор.
        self.assertEqual(list(islice(PrimeIterator(), 20_000)),
                         list(islice(primes(), 20_000)))

    def test_iterator_protocol(self) -> None:
        iterator = PrimeIterator()
        self.assertIsInstance(iterator, Iterator)
        self.assertIs(iter(iterator), iterator)

    def test_works_where_iterables_are_expected(self) -> None:
        found = []
        for prime in PrimeIterator():
            if prime > 20:
                break
            found.append(prime)
        self.assertEqual(found, [2, 3, 5, 7, 11, 13, 17, 19])
        self.assertEqual(list(zip("abc", PrimeIterator())),
                         [("a", 2), ("b", 3), ("c", 5)])

    def test_continues_where_it_stopped(self) -> None:
        iterator = PrimeIterator()
        self.assertEqual([next(iterator) for _ in range(4)], [2, 3, 5, 7])
        self.assertEqual(list(islice(iterator, 3)), [11, 13, 17])
        self.assertEqual(next(iterator), 19)

    def test_iterators_are_independent(self) -> None:
        first, second = PrimeIterator(), PrimeIterator()
        next(first)
        next(first)
        self.assertEqual(next(second), 2)
        self.assertEqual(next(first), 5)

    def test_memory_grows_with_root_not_with_count(self) -> None:
        # Та же оценка памяти, что у генератора (см. test_primes).
        tracemalloc.start()
        try:
            last = deque(islice(PrimeIterator(), 100_000), maxlen=1)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual(last[0], 1_299_709)
        self.assertLess(peak, 200_000)


if __name__ == "__main__":
    unittest.main()
