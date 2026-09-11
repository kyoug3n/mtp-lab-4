"""Тесты генератора простых чисел (Средн. 6)."""
import inspect
import tracemalloc
import unittest
from collections import deque
from itertools import islice, takewhile

from funclab.primes import primes


def is_prime(number: int) -> bool:
    """Наивная проверка делением — независимый эталон для сверки."""
    return number >= 2 and all(
        number % divisor for divisor in range(2, int(number ** 0.5) + 1)
    )


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

    def test_memory_grows_with_root_not_with_count(self) -> None:
        # 100 000 простых (последнее — 1 299 709) проходятся без хранения.
        # Решету нужны только простые до √1 299 709 ≈ 1140 — их меньше
        # двухсот. Один только список всех 100 000 чисел занял бы
        # несколько мегабайт; порог в 200 КБ оставляет большой запас.
        tracemalloc.start()
        try:
            last = deque(islice(primes(), 100_000), maxlen=1)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual(last[0], 1_299_709)
        self.assertLess(peak, 200_000)

    def test_generators_are_independent(self) -> None:
        first, second = primes(), primes()
        self.assertEqual([next(first) for _ in range(5)], [2, 3, 5, 7, 11])
        self.assertEqual(next(second), 2)
        self.assertEqual(next(first), 13)


if __name__ == "__main__":
    unittest.main()
